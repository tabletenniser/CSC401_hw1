#!/bin/sh
for num in {1..10}
do
    train_file="3.4_cv"$num"_train.arff"
    test_file="3.4_cv"$num"_validate.arff"
    # cmd "java -cp weka/weka.jar weka.classifiers.bayes.NaiveBayes -t 3.4_cv"$num"_train.arff -T 3.4_cv"$num"_validate.arff"
    echo "java -cp weka/weka.jar weka.classifiers.bayes.NaiveBayes -t 3.4_cv"$num"_train.arff -T 3.4_cv"$num"_validate.arff"
    OUTPUT="$(java -cp weka/weka.jar weka.classifiers.bayes.NaiveBayes -t $train_file -T $test_file)"
    # OUTPUT="$(ssh $host who)"
    echo "$OUTPUT"
done
