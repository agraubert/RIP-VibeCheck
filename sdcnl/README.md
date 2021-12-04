# SDCNL

This directory contains code for running SDCNL. This is based on the original
[SDCNL](https://github.com/ayaanzhaque/SDCNL) by Ayaan Haque. The publicly
available code was in an incomplete state, so we have made extensive modifications

## Dependencies

The dependencies for SDCNL are complex and not clearly listed. You can infer the
requirements by reading our SDCNL [Dockerfile](https://github.com/agraubert/RIP-VibeCheck/blob/main/docker/Dockerfile),
but we recommend just running it in our premade, public docker image `agraubert/sdcnl`.

## Training the model

Inside the docker container, you can run the following command to train SDCNL

```
python SDCNL/train_model.py SDCNL/data/training-set.csv
```

## Making predictions

After you have trained the model, you can make predictions by copying your own
data into the docker container. The only requirement is that your data be a csv
file with comment text in the `selftext` column. Predictions will be made by
adding a `suicide_p` column to the original csv, representing SDCNL's prediction
of how likely it is that the comment author is suicidal. To make predictions,
run the following command:

```
python SDCNL/make_prediction.py {your data}
```
