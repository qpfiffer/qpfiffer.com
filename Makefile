
all:
	$(CC) main.c -o qpfiffer.com -l38moths -O3

clean:
	rm -f *.o
	rm -f qpfiffer.com
