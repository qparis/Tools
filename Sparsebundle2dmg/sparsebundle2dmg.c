#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>

/* Quick & dirty tool to convert Apple sparsebundles to dmg.  */
/* Made by Quentin PÂRIS */
/* http://www.qparis.fr */
/* Licence : GPLv3 */

/* Usage : sparsebundle2img [input] [output] */

off_t blockSizeRead = 0; /* Default sparsebundle band size. But we should read the .plist file in fact */
off_t end = 0; 

off_t last_read = -1;
off_t last_write = -1;


char *filenameRead;
FILE* fdRead = NULL;

FILE* fdWrite = NULL;


int file_exists (char * fileName)
{
	struct stat buf;
	int i = stat ( fileName, &buf );
	if ( i == 0 )
	{
		return 1;
	}
	return 0;
}

void openBandR(off_t bandNum, char * sparseBundle)
{
	if(fdRead != NULL)
	{
		fclose(fdRead);
	}
	asprintf(&filenameRead, "%s/bands/%x", sparseBundle, bandNum);
	last_read = bandNum;
	fdRead = fopen(filenameRead, "r");
}

int readOffset(off_t offset, char * sparseBundle)
{
	
	off_t bandNum = offset / blockSizeRead;
	off_t bandOffset = offset % blockSizeRead;

	if(last_read != bandNum)
	{
		openBandR(bandNum, sparseBundle);	
	}
	int current = 0;
	
	if(fdRead == NULL)
	{
		return 0;
	}
	else
	{
		fseek(fdRead, bandOffset, SEEK_SET);
		current = fgetc(fdRead);
		return current;
	}
}

int writeOffset(int byte)
{
	char *filename;	
	if(fdWrite != NULL)
	{	
		fputc(byte, fdWrite);
		return 0;
	}
	else
	{
		return 2;
	}
	return 1;
}
void removeTag(char *line) /* Equivalent of php strip_tags */
{
	int copy = 1;
	char copyContent[255] = "";
	int i = 0;
	int j = 0;
	while(line[i] != '\0')
	{
		if(i > 255)
		{
			break;
		};
		if(j > 255)
		{
			break;
		};
		if(line[i] == '<')
		{
			copy = 0;
		}
		if(line[i] == '>')
		{
			copy = 1;
			i++;
		}
		if(copy == 1)
		{
			copyContent[j] = line[i];
			j++;
		}
		i++;
	}
	strcpy(line, copyContent);
}
static inline int read_plist(char *sparse)
{
	FILE* fd = NULL;
	char *plistName;
	asprintf(&plistName, "%s/Info.plist", sparse);
	fd = fopen(plistName, "r");
	char line[255] = "";

	char *sLine;
	if(fd == NULL)
	{
		return 1;
	}
	else
	{
		while(fgets(line, 255, fd) != NULL)
		{
			sLine = strstr(line, "<key>band-size</key>");
			if(sLine != NULL)
			{
				if(fgets(line, 255, fd) != NULL) /* We read the following line... */
				{
					removeTag(sLine);
					blockSizeRead = atoi(sLine);
				}
			}

			sLine = strstr(line, "<key>size</key>");
			if(sLine != NULL)
			{
				if(fgets(line, 255, fd) != NULL) /* We read the following line... */
				{
					removeTag(sLine);
					end = atoi(sLine);
				}
			}
		}
	}
	return 0;
}
int main( int argc, char *argv[] )
{

	if ( argc != 3 ) /* argc should be 2 for correct execution */
	{
		printf( "Usage: %s [input] [output]\n", argv[0] );
		return 0;
	}
	if(!file_exists(argv[1]))
	{
		printf("Error: File does not exist: %s. Aborting\n", argv[1]);
		return 1;
	}
	else
	{
		printf("Reading sparsebundle file: %s\n",argv[1]);
	}
	if(file_exists(argv[2]))
	{
		printf("Error: File exists: %s. Aborting\n", argv[2]);
		return 1;
	}
	else
	{
		printf("Writting content to: %s\n",argv[2]);
	}

	if(read_plist(argv[1]) == 1)
	{
		printf("Unable to open plist file! Aborting\n");
		return 1;
	}
	else
	{
		printf("Opening %s/Info.plist\n",argv[1]);
	}

	if(blockSizeRead == 0 || end == 0)
	{
		printf("Error while parsing plist file. Aborting\n");
		return 1;
	}
	else
	{
		printf("Block size: %ld\nImage size: %ld\n",blockSizeRead, end);
	}



	/* Open .dmg file to be created */
	fdWrite = fopen(argv[2], "a+");

	off_t i = 0;
	int last_perc = 0;
	int perc;
	for(i = 0; i < end; i++)
	{
		if(writeOffset(readOffset(i,argv[1])) == 2)
		{
			printf("Fatal error when writting file. Aborting\n");
			return 2;
		}
		perc = i * 100 / end;
		if(perc != last_perc)
		{
			printf("%d/100 completed\n",perc);
			last_perc = perc;
		}
	}
	if(last_perc != 100)
		printf("100/100 completed\n");
	
	fclose(fdRead);
	fclose(fdWrite);

	return 0;
}
