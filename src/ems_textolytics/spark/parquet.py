import random

import pyspark as spark

from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .master("local") \
    .appName("Word Count") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()

data = []
for x in range(5):
    data.append((random.randint(0,9), random.randint(0,9)))
df = spark.createDataFrame(data, ("label", "data"))

df.show()


#Write data in gzip compressed data in parquet format
# path_parquet_gzip = "/prueba_gzip.parquet"# Read from HDFS
path_parquet_gzip = "E:\data\parquet"""

# Read from local file

df.write \
    .mode("append") \
    .format("parquet") \
    .option("compression", "gzip") \
    .save(path_parquet_gzip)



#Read gzip compressed data in parquet format
df2 = spark \
    .read \
    .option("multiline", "true") \
    .parquet(path_parquet_gzip)

df2.show()

# df.write.mode('append').parquet('parquet_data_file')
