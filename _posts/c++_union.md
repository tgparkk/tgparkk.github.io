union 은 변수 중 가장 큰 변수의 메모리를 공유

struct 는 각각의 변수 크기를 고려해 메모리 할당


구조체 비트 필드
struct Flags {
    unsigned int a : 1;    // a는 1비트 크기  
    unsigned int b : 3;    // b는 3비트 크기  
    unsigned int c : 7;    // c는 7비트 크기  
};
