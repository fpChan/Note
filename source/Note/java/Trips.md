# Java 常用代码

## File 操作

#### 文件转换成byte数组

```java
String filePath = "/temp/abc.txt";

byte[] bFile = Files.readAllBytes(new File(filePath).toPath());
//or this
byte[] bFile = Files.readAllBytes(Paths.get(filePath));

```

####byte数组转换成文件

```java
Path path = Paths.get(fileDest);

Files.write(path, bytesArray);
```



