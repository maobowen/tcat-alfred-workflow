# TCAT Next Bus

**TCAT Next Bus** is an Alfred workflow for querying departure time of [Tompkins Consolidated Area Transit (TCAT)](https://www.tcatbus.com) buses in Tompkins County, New York. It runs on [Alfred 3](https://www.alfredapp.com) with [Alfred Powerpack](https://www.alfredapp.com/powerpack/) enabled. It has never been so easy to track TCAT buses on your Mac!

## Installation

Download the [latest release](https://github.com/maobowen/tcat-alfred-workflow/releases/latest), and double-click it to install.

## Usage

Use the keyword `tc` to start a query. You can either enter a stop ID (e.g., "100" for Ithaca Commons - Seneca Street Station) or a phrase (e.g., "commons") to see the departure schedule of a bus stop.

Enter `tc 100` to see the schedule of Ithaca Commons - Seneca Street Station directly:  
![Demonstration of querying by stop ID](https://github.com/maobowen/tcat-alfred-workflow/raw/master/demo/demo1.gif)

Enter `tc commons` to get a list of bus stops whose names contain the phrase "commons". Then select a stop from the list, and press <kbd>tab</kbd> key to get the schedule of that stop:  
![Demonstration of querying by keywords](https://github.com/maobowen/tcat-alfred-workflow/raw/master/demo/demo2.gif)

## Acknowledgement

This project is powered by [Alfred-Workflow](https://github.com/deanishe/alfred-workflow), a helper library in Python for authors of workflows for Alfred 2 and 3.

***
&copy; 2019 [Bowen Mao](https://bmao.tech/).