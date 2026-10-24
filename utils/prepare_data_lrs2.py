"""
The .csv preperation functions for WSJ0-Mix.

Author
 * Cem Subakan 2020

 """

import os
import csv
import json


def prepare_lrs2(
    datapath,
    savepath,
    n_spks=2,
    skip_prep=False,
    fs=8000,
    source_sample_rate=16000,
    version="min",
):
    """Prepare static LRS2-2Mix CSVs; resampling happens during audio loading."""
    if skip_prep:
        return
    if n_spks != 2:
        raise ValueError("LRS2-2Mix requires n_spks=2")
    if source_sample_rate not in (8000, 16000):
        raise ValueError("LRS2 source_sample_rate must be 8000 or 16000")
    if version not in ("min", "max"):
        raise ValueError("LRS2 version must be 'min' or 'max'")
    os.makedirs(savepath, exist_ok=True)
    create_wsj_csv(datapath, savepath, source_sample_rate, version)


def prepare_wsjmix(
    datapath,
    savepath,
    n_spks=2,
    skip_prep=False,
    librimix_addnoise=False,
    fs=8000,
):
    """
    Prepared wsj2mix if n_spks=2 and wsj3mix if n_spks=3.

    Arguments:
    ----------
        datapath (str) : path for the wsj0-mix dataset.
        savepath (str) : path where we save the csv file.
        n_spks (int): number of speakers
        skip_prep (bool): If True, skip data preparation
        librimix_addnoise: If True, add whamnoise to librimix datasets
    """

    if skip_prep:
        return

    # if "LibriMix" in datapath:

    if n_spks == 2:
        # assert (
        #     "2speakers" in datapath
        # ), "Inconsistent number of speakers and datapath"
        create_wsj_csv(datapath, savepath)
    elif n_spks == 3:
        assert (
            "3speakers" in datapath
        ), "Inconsistent number of speakers and datapath"
        create_wsj_csv_3spks(datapath, savepath)
    else:
        raise ValueError("Unsupported Number of Speakers")
    # else:
    #     print("Creating a csv file for a custom dataset")
    #     create_custom_dataset(datapath, savepath)


def create_custom_dataset(
    datapath,
    savepath,
    dataset_name="custom",
    set_types=["train", "valid", "test"],
    folder_names={
        "source1": "source1",
        "source2": "source2",
        "mixture": "mixture",
    },
):
    """
    This function creates the csv file for a custom source separation dataset
    """

    for set_type in set_types:
        mix_path = os.path.join(datapath, set_type, folder_names["mixture"])
        s1_path = os.path.join(datapath, set_type, folder_names["source1"])
        s2_path = os.path.join(datapath, set_type, folder_names["source2"])

        files = os.listdir(mix_path)

        mix_fl_paths = [os.path.join(mix_path, fl) for fl in files]
        s1_fl_paths = [os.path.join(s1_path, fl) for fl in files]
        s2_fl_paths = [os.path.join(s2_path, fl) for fl in files]

        csv_columns = [
            "ID",
            "duration",
            "mix_wav",
            "mix_wav_format",
            "mix_wav_opts",
            "s1_wav",
            "s1_wav_format",
            "s1_wav_opts",
            "s2_wav",
            "s2_wav_format",
            "s2_wav_opts",
            "noise_wav",
            "noise_wav_format",
            "noise_wav_opts",
        ]

        with open(
            os.path.join(savepath, dataset_name + "_" + set_type + ".csv"), "w"
        ) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for i, (mix_path, s1_path, s2_path) in enumerate(
                zip(mix_fl_paths, s1_fl_paths, s2_fl_paths)
            ):

                row = {
                    "ID": i,
                    "duration": 1.0,
                    "mix_wav": mix_path,
                    "mix_wav_format": "wav",
                    "mix_wav_opts": None,
                    "s1_wav": s1_path,
                    "s1_wav_format": "wav",
                    "s1_wav_opts": None,
                    "s2_wav": s2_path,
                    "s2_wav_format": "wav",
                    "s2_wav_opts": None,
                }
                writer.writerow(row)


def create_wsj_csv(datapath, savepath, source_sample_rate=16000, version="min"):
    """
    This function creates the csv files to get the speechbrain data loaders for the wsj0-2mix dataset.

    Arguments:
        datapath (str) : path for the wsj0-mix dataset.
        savepath (str) : path where we save the csv file
    """

    for set_type in ["tr", "cv", "tt"]:
        split_path = os.path.join(
            datapath, f"wav{source_sample_rate // 1000}k", version, set_type
        )
        mix_path = os.path.join(split_path, "mix", "")
        s1_path = os.path.join(split_path, "s1", "")
        s2_path = os.path.join(split_path, "s2", "")

        files = sorted(fl for fl in os.listdir(mix_path) if fl.lower().endswith(".wav"))
        if not files:
            raise ValueError(f"No WAV files found in {mix_path}")
        for fl in files:
            for folder in (mix_path, s1_path, s2_path):
                path = os.path.join(folder, fl)
                if not os.path.isfile(path):
                    raise FileNotFoundError(path)

        mix_fl_paths = [mix_path + fl for fl in files]
        s1_fl_paths = [s1_path + fl for fl in files]
        s2_fl_paths = [s2_path + fl for fl in files]

        csv_columns = [
            "ID",
            "duration",
            "mix_wav",
            "mix_wav_format",
            "mix_wav_opts",
            "s1_wav",
            "s1_wav_format",
            "s1_wav_opts",
            "s2_wav",
            "s2_wav_format",
            "s2_wav_opts",
        ]

        with open(os.path.join(savepath, f"lrs2_{set_type}.csv"), "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for i, (mix_path, s1_path, s2_path) in enumerate(
                zip(mix_fl_paths, s1_fl_paths, s2_fl_paths)
            ):

                row = {
                    "ID": i,
                    "duration": 1.0,
                    "mix_wav": mix_path,
                    "mix_wav_format": "wav",
                    "mix_wav_opts": None,
                    "s1_wav": s1_path,
                    "s1_wav_format": "wav",
                    "s1_wav_opts": None,
                    "s2_wav": s2_path,
                    "s2_wav_format": "wav",
                    "s2_wav_opts": None,
                }
                writer.writerow(row)


def create_wsj_csv_3spks(datapath, savepath):
    """
    This function creates the csv files to get the speechbrain data loaders for the wsj0-3mix dataset.

    Arguments:
        datapath (str) : path for the wsj0-mix dataset.
        savepath (str) : path where we save the csv file
    """
    for set_type in ["tr", "cv", "tt"]:
        mix_path = os.path.join(datapath, "wav8k/min/" + set_type + "/mix/")
        s1_path = os.path.join(datapath, "wav8k/min/" + set_type + "/s1/")
        s2_path = os.path.join(datapath, "wav8k/min/" + set_type + "/s2/")
        s3_path = os.path.join(datapath, "wav8k/min/" + set_type + "/s3/")

        files = os.listdir(mix_path)

        mix_fl_paths = [mix_path + fl for fl in files]
        s1_fl_paths = [s1_path + fl for fl in files]
        s2_fl_paths = [s2_path + fl for fl in files]
        s3_fl_paths = [s3_path + fl for fl in files]

        csv_columns = [
            "ID",
            "duration",
            "mix_wav",
            "mix_wav_format",
            "mix_wav_opts",
            "s1_wav",
            "s1_wav_format",
            "s1_wav_opts",
            "s2_wav",
            "s2_wav_format",
            "s2_wav_opts",
            "s3_wav",
            "s3_wav_format",
            "s3_wav_opts",
        ]

        with open(savepath + "/wsj_" + set_type + ".csv", "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for i, (mix_path, s1_path, s2_path, s3_path) in enumerate(
                zip(mix_fl_paths, s1_fl_paths, s2_fl_paths, s3_fl_paths)
            ):

                row = {
                    "ID": i,
                    "duration": 1.0,
                    "mix_wav": mix_path,
                    "mix_wav_format": "wav",
                    "mix_wav_opts": None,
                    "s1_wav": s1_path,
                    "s1_wav_format": "wav",
                    "s1_wav_opts": None,
                    "s2_wav": s2_path,
                    "s2_wav_format": "wav",
                    "s2_wav_opts": None,
                    "s3_wav": s3_path,
                    "s3_wav_format": "wav",
                    "s3_wav_opts": None,
                }
                writer.writerow(row)
