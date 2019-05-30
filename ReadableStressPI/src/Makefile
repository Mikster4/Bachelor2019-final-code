CC = g++

clean:
	rm ../bin/FEBioReadableStress.so

all :
	$(CC) -fPIC -I../../../FEBio2 FEBioReadableStress.cpp dllmain.cpp -shared -o ../bin/FEBioReadableStress.so
