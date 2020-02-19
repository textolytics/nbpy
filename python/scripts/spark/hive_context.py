from pyspark.sql import SparkSession
import os
os.listdir(os.getcwd())
spark = SparkSession.builder.enableHiveSupport().getOrCreate()
spark.sql('show databases').show()