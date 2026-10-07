"""Shared figure palette approved October 4, 2026 (original dark green and rust restored).

The HTML book uses the white theme. Dark values retain the legacy companion
assets for reproducibility; they are not an additional approved page theme.
"""


def palette(mode="light"):
    light = dict(
        paper="#FFFFFF", ink="#2B302D", muted="#616962", grid="#E1E5DF",
        primary="#3D6155", comparison="#A36F49", third="#758C7F", fourth="#B39B61",
        education_dropout="#827568", education_highschool="#6F887A",
        education_somecollege="#66726B",
        sequential=["#A36F49", "#C49A77", "#E5D4BD"],
    )
    dark = dict(
        paper="#202522", ink="#E5EBE6", muted="#B6C0B8", grid="#414942",
        primary="#ACC9BB", comparison="#D9A278", third="#C0CFC5", fourth="#D0BC8F",
        education_dropout="#B9ACA0", education_highschool="#BDCCC3",
        education_somecollege="#CFD3CE",
        sequential=["#D9A278", "#A77957", "#685440"],
    )
    return (dark if mode == "dark" else light).copy()
