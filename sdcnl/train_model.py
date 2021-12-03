import argparse
import os
import tempfile
import subprocess
import sys
import pandas as pd


def run_cmd(cmd):
    print(cmd)
    subprocess.check_call(cmd, shell=True, executable='/bin/bash')

if __name__ == "__main__":
    parser = argparse.ArgumentParser('SDCNL-Train', description="Master model-training script")
    parser.add_argument('training', help="input reddit training data")
    parser.add_argument('-m', '--model', help="Model filename. Defaults to model.h5", default='model.h5')
    parser.add_argument(
        '-t', '--text-column',
        help="Column for comment text. Must be the same between training and testing data Default: selftext",
        default='selftext'
    )
    parser.add_argument(
        '-l', '--label-column',
        help='Column for training labels. Must be the same between training and testind data. Default: is_suicide',
        default='is_suicide'
    )
    parser.add_argument(
        '--test',
        help="File to testing data. If not provided, no tests will be run",
        default=None
    )

    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tempdir:
        print("Generating training embeddings")

        run_cmd(
            '{} {}/word_embeddings.py {} {}/training_embeddings.csv'.format(
                sys.executable,
                os.path.dirname(__file__),
                args.training,
                tempdir
            )
        )

        if args.test:
            print("Generating testing embeddings")
            run_cmd(
                '{} {}/word_embeddings.py {} {}/testing_embeddings.csv'.format(
                    sys.executable,
                    os.path.dirname(__file__),
                    args.test,
                    tempdir
                )
            )

        # FIXME: Clustering

        print("Training model")
        run_cmd(
            '{} {}/classifiers.py {} {}/training_embeddings.csv -m {} -l {}'.format(
                sys.executable,
                os.path.dirname(__file__),
                args.training,
                tempdir,
                args.model,
                args.label_column
            )
        )

        print("Checking Training accuracy")
        run_cmd(
            '{} {}/predictor.py {}/training_embeddings.csv {}/training_predictions.csv -m {}'.format(
                sys.executable,
                os.path.dirname(__file__),
                tempdir,
                tempdir,
                args.model
            )
        )

        if args.test:
            print("Checking Training accuracy")
            run_cmd(
                '{} {}/predictor.py {}/testing_embeddings.csv {}/testing_predictions.csv -m {}'.format(
                    sys.executable,
                    os.path.dirname(__file__),
                    tempdir,
                    tempdir,
                    args.model
                )
            )

            testing_labels = pd.read_csv(args.test)[args.label_column]
            test_pred_labels = pd.read_csv('{}/testing_predictions.csv'.format(tempdir))['0']

        training_labels = pd.read_csv(args.training)[args.label_column]
        predicted_labels = pd.read_csv('{}/training_predictions.csv'.format(tempdir))['0']

        print("Training accuracy:", (training_labels == (predicted_labels >= 0.5)).mean())
        if args.test:
            print("Testing accuracy:", (testing_labels == (test_pred_labels >= 0.5)).mean())
