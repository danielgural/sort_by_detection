## Sort By Detections!

![sort_by_detection](https://github.com/danielgural/sort_by_detection/blob/main/assets/sort_detections.gif)

This plugin is a Python plugin that allows for you sort your samples based on detections!

See your dataset in a whole new light!

## Installation

```shell
fiftyone plugins download https://github.com/danielgural/sort_by_detection
```

## Operators

### `sort_by_detections`

Sorts based on a the selected feature. Today, only sorting by the number of detections is supported. The plugin allows you to sort based on any of your detection fields as well as having the option to sort based on all the detections on the sample or by only a specific class. Sorting in reverse will return the sort from highest to lowest. Only samples that contain the detection will be returned if returning by a class. The filters can be stacked if ran multiple times as well!
