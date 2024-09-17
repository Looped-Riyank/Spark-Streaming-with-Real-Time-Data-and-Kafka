from __future__ import print_function
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split

from kafka import KafkaProducer

bootstrap_servers = ['localhost:9092']
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
producer = KafkaProducer()
outputTopic = 'topic2'

from kafka import KafkaConsumer

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("""
        Usage: consumer.py <bootstrap-servers> <subscribe-type> <topics>
        """, file=sys.stderr)
        sys.exit(-1)

    bootstrapServers = sys.argv[1]
    subscribeType = sys.argv[2]
    topics = sys.argv[3]

    spark = SparkSession \
        .builder \
        .appName("MapReduceWordCount") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    # Create DataSet representing the stream of input lines from kafka
    lines = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrapServers) \
        .option(subscribeType, topics) \
        .load() \
        .selectExpr("CAST(value AS STRING)")

    # Split the lines into words
    words = lines.select(
        # explode turns each item in an array into a separate row
        explode(
            split(lines.value, ' ')
        ).alias('word')
    )

    # Generate running word count
    wordCounts = words.groupBy('word').count()

    query = wordCounts \
        .selectExpr("CAST(word AS STRING) AS key", "to_json(struct(*)) AS value") \
        .writeStream \
        .trigger(processingTime="10 seconds") \
        .outputMode("update") \
        .format("kafka") \
        .option("topic", outputTopic) \
        .option("kafka.bootstrap.servers", bootstrapServers) \
        .option("checkpointLocation", "./checkpoint") \
        .start()

    query.awaitTermination()
