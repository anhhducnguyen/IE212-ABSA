# import findspark
# findspark.init()

# import pyspark
# from pyspark.sql import SparkSession
# from pyspark.sql.types import StructType, StructField, StringType, IntegerType
# from pyspark.sql.functions import col, from_json
# import requests

# scala_version = '2.12'  # your scala version
# spark_version = '3.2.3' # your spark version
# kafka_version = '2.5.0' # your kafka version
# spark_nlp_version = '5.2.3'

# packages = [
#     f'org.apache.spark:spark-sql-kafka-0-10_{scala_version}:{spark_version}',
#     f'org.apache.kafka:kafka-clients:{kafka_version}',
#     f'com.johnsnowlabs.nlp:spark-nlp_2.12:{spark_nlp_version}'
# ]

# spark = SparkSession.builder \
#                     .appName("kafka-shopee")\
#                     .master("local[4]")\
#                     .config("spark.python.worker.reuse",True) \
#                     .config("spark.executor.memory", "16g") \
#                     .config("spark.driver.memory", "16g") \
#                     .config("spark.driver.maxResultSize", "0") \
#                     .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
#                     .config("spark.kryoserializer.buffer.max", "2000M") \
#                     .config("spark.sql.adaptive.enabled", False) \
#                     .config("spark.sql.execution.arrow.maxRecordsPerBatch", "16") \
#                     .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", True) \
#                     .config("spark.jars.packages", ",".join(packages))\
#                     .config("spark.executor.heartbeatInterval", "3600s") \
#                     .config("spark.network.timeout", "4000s") \
#                     .getOrCreate()

# spark.sparkContext.setLogLevel("error")

# print(packages)

# from preprocess import udf_clean
# from pipeline import pipeline

# topic_name = 'ryhjlimi-shopee'
# kafka_server = 'localhost:9092'

# streamRawDf = spark\
#                 .readStream\
#                 .format("kafka")\
#                 .option("kafka.bootstrap.servers", kafka_server)\
#                 .option("subscribe", topic_name)\
#                 .option("startingOffsets", "latest")\
#                 .option("kafka.security.protocol", "SASL_SSL")\
#                 .option("kafka.sasl.mechanism", "SCRAM-SHA-256")\
#                 .option("kafka.sasl.jaas.config", "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"ryhjlimi\" password=\"LuUoqLhDxrLrFDGjJPDxoaW1i4lnKaOl\";")\
#                 .option("failOnDataLoss", "false") \
#                 .option("groupIdPrefix", "ryhjlimi-") \
#                 .option('spark.default.parallelism', 1) \
#                 .option('spark.sql.shuffle.partitions', 1) \
#                 .load()

# # Define the JSON schema
# json_schema = StructType([
#     StructField("cmtid", StringType(), True),
#     StructField("comment", StringType(), True),
#     StructField("rating_star", IntegerType(), True),
# ])

# streamDF = streamRawDf \
#     .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
#     .select(from_json("value", json_schema).alias("data")) \
#     .select("data.*")

# cleanDF = streamDF\
#     .withColumn("text", udf_clean(col('comment')))\

# resultDF = pipeline.fit(cleanDF).transform(cleanDF)

# # Define a function to send individual records to the localhost server
# def send_record_to_server(record):
#     url = "http://127.0.0.1:5000/"

#     try:
#         response = requests.post(url, json=record.asDict())
#     except:
#         pass

# from dotenv import load_dotenv
# load_dotenv()

# import os
# output_path = os.getenv('ROOT_PATH') + "/database/"
# if (not os.path.exists(output_path)):
#     os.mkdir(output_path)

# checkpoint_location = os.getenv('ROOT_PATH') + "/database/checkpoint/"

# stream_writer = (
#     resultDF
#     .writeStream 
#     .queryName("predictComments") 
#     .outputMode("append")
#     .format("csv")
#     .option("path", output_path) 
#     .option("checkpointLocation", checkpoint_location) 
#     .option("truncate", False)
#     .option("header", True)
#     .foreach(send_record_to_server)
#     .trigger(processingTime="10 seconds") 
# )

# query = stream_writer.start()
# query.awaitTermination()

import findspark
findspark.init()

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import col, from_json
import requests

# Thông tin cấu hình
scala_version = '2.12'  # Phiên bản scala của bạn
spark_version = '3.2.3' # Phiên bản Spark của bạn
kafka_version = '3.9.0' # Phiên bản Kafka của bạn
spark_nlp_version = '5.2.3'

packages = [
    f'org.apache.spark:spark-sql-kafka-0-10_{scala_version}:{spark_version}',
    f'org.apache.kafka:kafka-clients:{kafka_version}',
    f'com.johnsnowlabs.nlp:spark-nlp_2.12:{spark_nlp_version}'
]

# Tạo SparkSession
spark = SparkSession.builder \
                    .appName("kafka-shopee")\
                    .master("local[4]")\
                    .config("spark.python.worker.reuse",True) \
                    .config("spark.executor.memory", "16g") \
                    .config("spark.driver.memory", "16g") \
                    .config("spark.driver.maxResultSize", "0") \
                    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                    .config("spark.kryoserializer.buffer.max", "2000M") \
                    .config("spark.sql.adaptive.enabled", False) \
                    .config("spark.sql.execution.arrow.maxRecordsPerBatch", "16") \
                    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", True) \
                    .config("spark.jars.packages", ",".join(packages))\
                    .config("spark.executor.heartbeatInterval", "3600s") \
                    .config("spark.network.timeout", "4000s") \
                    .getOrCreate()

spark.sparkContext.setLogLevel("error")

# Import các thư viện cần thiết
from preprocess import udf_clean
from pipeline import pipeline

# Kafka cấu hình
topic_name = 'ryhjlimi-shopee'
kafka_server = 'localhost:9092'  # Địa chỉ Kafka trên local

# Đọc dữ liệu từ Kafka
streamRawDf = spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", kafka_server) \
                .option("subscribe", topic_name) \
                .option("startingOffsets", "latest") \
                .option("failOnDataLoss", "false") \
                .option("groupIdPrefix", "ryhjlimi-") \
                .option('spark.default.parallelism', 1) \
                .option('spark.sql.shuffle.partitions', 1) \
                .load()

# Định nghĩa schema cho dữ liệu JSON
json_schema = StructType([
    StructField("cmtid", StringType(), True),
    StructField("comment", StringType(), True),
    StructField("rating_star", IntegerType(), True),
])

# Chuyển đổi dữ liệu từ Kafka
streamDF = streamRawDf \
    .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .select(from_json("value", json_schema).alias("data")) \
    .select("data.*")

# Làm sạch dữ liệu
cleanDF = streamDF \
    .withColumn("text", udf_clean(col('comment')))

# Áp dụng pipeline (nếu có)
resultDF = pipeline.fit(cleanDF).transform(cleanDF)

# Định nghĩa hàm gửi dữ liệu tới server
def send_record_to_server(record):
    url = "http://127.0.0.1:5000/"
    try:
        response = requests.post(url, json=record.asDict())
    except:
        pass

# Đọc các biến môi trường từ file .env
from dotenv import load_dotenv
load_dotenv()

# Đường dẫn lưu trữ dữ liệu
import os
output_path = os.getenv('ROOT_PATH') + "/database/"
if not os.path.exists(output_path):
    os.mkdir(output_path)

# Đường dẫn checkpoint
checkpoint_location = os.getenv('ROOT_PATH') + "/database/checkpoint/"

# Cấu hình ghi dữ liệu
stream_writer = (
    resultDF
    .writeStream 
    .queryName("predictComments") 
    .outputMode("append")
    .format("csv")
    .option("path", output_path) 
    .option("checkpointLocation", checkpoint_location) 
    .option("truncate", False)
    .option("header", True)
    .foreach(send_record_to_server)  # Gửi dữ liệu tới server
    .trigger(processingTime="10 seconds")  # Cập nhật dữ liệu mỗi 10 giây
)

# Bắt đầu stream
query = stream_writer.start()
query.awaitTermination()
