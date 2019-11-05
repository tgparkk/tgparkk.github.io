---
layout: post
title: "UNION-FIND"
author: tgparkk
categories: [CS, DATASTRUCTURE]
image: assets/images/자료구조.png
---

UNION-FIND

## UNION-FIND 

#### JAVA
```java
static int[]root=new int[200001];
static int[]rank=new int[200001];
static int[]node_count=new int[200001];
static void init(){
	for(int i=0;i<=200000;i++){
		root[i]=i;
		rank[i]=1;
		node_count[i]=1;
	}
}
static int find(int a){
	if(root[a]==a)return a;
	return root[a]=find(root[a]);
}
static void union(int a,int b){
	a=find(a);
	b=find(b);
	if(a==b)return;
	if(rank[a]<rank[b]){
		int tmp=a;
		a=b;
		b=tmp;
	}
	root[b]=a;
	node_count[a]+=node_count[b];
	if(rank[a]==rank[b])rank[a]++;
}

```


