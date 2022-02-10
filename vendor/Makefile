
SPNGDIR := libspng-0.7.1/
MINIZDIR := miniz-2.2.0/

all: spng 

spng: ${SPNGDIR}/spng.c ${MINIZDIR}/miniz.c
	gcc -O3 -c -DMINIZ_NO_STDIO=1 -DSPNG_USE_MINIZ=1 \
		-stdlib=libc++ -mmacosx-version-min=10.9 \
		-I${SPNGDIR} -I${MINIZDIR} libspng-0.7.1/spng.c miniz-2.2.0/miniz.c
	ar rcs libspng.a spng.o miniz.o
	rm *.o

clean:
	rm *.o *.a