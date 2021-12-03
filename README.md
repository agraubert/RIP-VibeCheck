# Mental Health Analysis Toolkit

The toolkit formerly known as Vibecheck by
Neeraj Alavala, Aaron Graubert, and Sean Walsh

## Overview

We started this project with the intent to provide a
robust mental health analysis pipeline to handle live
social media data. While we were unable to complete
this project within the semester, we still wanted to
organize our work so that others may continue from it
in the future. You can find our final report **FIXME**.

### Structure

* discord: This folder contains the start of a discord
scraper, however this project direction was abandoned for
various reasons, one of which being that SDCNL (the
  classifier chosen) was trained on reddit
* reddit: This folder contains code for our Reddit scrapers. Further information can be found in the reddit directory
* SDCNL: This folder contains code for SDCNL. Further information can be found in that directory

## Getting Started

To resume work on this project, we recommend that you
get the reddit scraper up and running first, so it can
build up a volume of live comments while you work on
other components. Detailed instructions can be found
in the README for the reddit directory.

After your scrapers are running, you can use SDCNL to
make calls on comments. SDCNL is built in a docker image
and the dockerfile is provided. You can also run our
version of the image: `agraubert/sdcnl`.

## Data Access

The following data can be made available upon request:
* Disk images for our data scraping and SDCNL VMs
* Snapshots of our Reddit database
* Buzzcard data obtained from Georgia Tech

To access any of this data, please reach out to Neeraj,
Sean, Aaron, or Professor Pu.
