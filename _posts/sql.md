[https://www.inflearn.com/course/%EC%84%B1%EB%8A%A5%EC%A2%8B%EC%9D%80-%EC%BF%BC%EB%A6%AC%EC%9E%91%EC%84%B1%EB%B2%95#reviews](https://www.inflearn.com/course/%EC%84%B1%EB%8A%A5%EC%A2%8B%EC%9D%80-%EC%BF%BC%EB%A6%AC%EC%9E%91%EC%84%B1%EB%B2%95#reviews)

- 인덱스 검색, Index Seek 는 정상적인 인덱스 사용중 이라는 표시
- Index Scan, 인덱스 스캔, 테이블 스캔 은 비정상적으로 사용중 이라는 표시 (화살표 모양 : 일직선)
![index](https://user-images.githubusercontent.com/45591830/219554509-33c661a0-4c09-4d4b-bf5f-7e426cbb9bc1.PNG)

![io](https://user-images.githubusercontent.com/45591830/219554813-38570e14-0254-4854-b620-8f8958348644.PNG)

- 교환법칙, 결합법칙 에 의해 optimizer 가 join 순서는 알아서 최적으로 해줍니다.
```sql

/*
---------------------------------------------------------------------
교환법칙, 결합법칙
---------------------------------------------------------------------
*/
/*
WHERE
*/
SELECT *
FROM dbo.[Order Details]
WHERE (Discount != 0)
AND (10 / Discount > 0)

   -- vs.
   SELECT *
   FROM dbo.[Order Details]
   WHERE (10 / Discount > 0)
   AND (Discount <> 0)


/*
JOIN
*/
SELECT *
FROM dbo.Orders AS o 
INNER JOIN dbo.[Order Details] AS d
   ON o.OrderID = d.OrderID
WHERE o.OrderID = 10249

   -- vs.
   SELECT *
   FROM dbo.[Order Details] AS d
   INNER JOIN dbo.Orders AS o 
      ON d.OrderID = o.OrderID
   WHERE d.OrderID = 10249
```
