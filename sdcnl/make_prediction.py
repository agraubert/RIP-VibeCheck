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
    parser = argparse.ArgumentParser('SDCNL-Predict', description="Master model-training script")
    parser.add_argument('input', help="input reddit training data")
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

    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tempdir:
        print("Generating embeddings")

        run_cmd(
            '{} {}/word_embeddings.py {} {}/embeddings.csv'.format(
                sys.executable,
                os.path.dirname(__file__),
                args.training,
                tempdir
            )
        )

        print("Checking Training accuracy")
        run_cmd(
            '{} {}/predictor.py {}/embeddings.csv {}/predictions.csv -m {}'.format(
                sys.executable,
                os.path.dirname(__file__),
                tempdir,
                tempdir,
                args.model
            )
        )

        df = pd.read_csv(args.training)
        pred = pd.read_csv('{}/predictions.csv'.format(tempdir))['0']
        df['suicide_p'] = pred.values
        df.to_csv(args.training)
