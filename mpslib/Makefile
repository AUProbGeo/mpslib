INCLUDES = -I.
SRC_DIR = .

SRCS = $(wildcard $(SRC_DIR)/*.cpp)

%.o : $(SRC_DIR)/%.cpp
	$(CXX) -fPIC -o $@ $(INCLUDES) $(CPPFLAGS) -c $^

all : mpslib.a

mpslib.a : $(SRCS:.cpp=.o) 
	$(AR) rsv $@ $^

clean:
	rm -f *.o *.a

