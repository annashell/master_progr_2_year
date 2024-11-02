import sqlite3

from pyspark.sql.connect.functions import stddev
from pyspark.sql.functions import avg

db_path = r"D:\projects\master_progr_2_year\scripts\big_data\corpres_seg.db"

sqlite_connection = sqlite3.connect(db_path)
cursor = sqlite_connection.cursor()

cursor.execute('select * from f0')
rows = cursor.fetchall()

with open("f0.csv", 'w', encoding="UTF-8") as f:
    # f.write("id,filename,unit,start,end,alloph_index,seg_index,duration\n")
    for row in rows:
        new_str = ""
        for field in row:
            new_str += str(field) + ','
        new_str += str(row[5] - row[4])
        f.write(new_str + '\n')


from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

prev = spark.read.csv(r'D:\projects\master_progr_2_year\scripts\big_data\f0.csv')

prev.show(2)

parsed = spark.read.option("header", "true")\
  .option("nullValue", "?")\
  .option("inferSchema", "true")\
  .csv(r'D:\projects\master_progr_2_year\scripts\big_data\f0.csv')


parsed.printSchema()


print(f"Всего записей: {parsed.count()}")

# средняя длина периода
parsed.agg(avg('_c7'), stddev("_c7")).show()