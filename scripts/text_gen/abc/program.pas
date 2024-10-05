function add10(x: integer): integer;
begin
    result := x + 10
end;


begin
    var a: integer;
    a: = ReadInteger();
    var b := ReadReal();
    print(a, b);
    println(a);
    println($'{a}###{b}')
end.