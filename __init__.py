import fiftyone as fo
import fiftyone.operators as foo
from fiftyone.operators import types
from fiftyone.brain import Similarity
from pprint import pprint
from fiftyone import ViewField as F


import fiftyone as fo
import fiftyone.operators as foo
from fiftyone.operators import types




class SortByDetections(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="sort_by_detections",
            label="Sort By Detections",
            description="Sorts your view or dataset by different features of your detections",
            icon="/assets/book.svg",
            dynamic=True,

        )
    
    def resolve_input(self, ctx):
        inputs = types.Object()
    
        ready = _sort_by_detections_inputs(ctx,inputs)

        if ready:
            _execution_mode(ctx, inputs)
        

        return types.Property(inputs)
    
    def resolve_delegation(self, ctx):
        return ctx.params.get("delegate", False)
    
    def execute(self, ctx):
        
        _sort_detections(ctx)
    
        return {}
    
def _sort_by_detections_inputs(ctx, inputs):

    target_view = get_target_view(ctx, inputs)

    sort_choices = ["Number of Detections", ] 

    sort_radio_group = types.RadioGroup()

    for choice in sort_choices:
        sort_radio_group.add_choice(choice, label=choice)

    inputs.enum(
    "sort_radio_group",
    sort_radio_group.values(),
    label="Sorting Style",
    description="Choose what to sort on:",
    view=types.DropdownView(),
    default='Number of Detections',
    required=False,
    )

    detections = []
    field_names = list(target_view.get_field_schema().keys())
    for name in field_names:
        if type(target_view.get_field(name)) == fo.core.fields.EmbeddedDocumentField:
            if "detections" in  list(target_view.get_field(name).get_field_schema().keys()):
                detections.append(name + ".detections") 

    if detections == []:
        inputs.view(
        "error", 
        types.Error(label="No Detections found on this dataset", description="Add detections to be able to sort by them")
    )
    else:

        det_radio_group = types.RadioGroup()

        for choice in detections:
            det_radio_group.add_choice(choice, label=choice)

        inputs.enum(
        "det_radio_group",
        det_radio_group.values(),
        label="Choose Field",
        description="Choose what detection field to sort on:",
        view=types.DropdownView(),
        required=True,
        default=None
        )

        inputs.bool(
        "sort_by_class",
        label="Sort by class?",
        description="Turn on sorting on a specific class or not.",
        view=types.SwitchView(),
        )

        by_class = ctx.params.get("sort_by_class", False)



        if by_class:

            field = ctx.params.get("det_radio_group")
            inputs.view(
                "error", 
                types.Error(label=field, description="Add detections to be able to sort by them")
            )
            if field == None:
                inputs.view(
                    "warning", 
                    types.Error(label="Choose a field first!", description="Pick a detection field to sort on first")
                )
            else:
                classes = target_view.distinct(field + ".label")
                class_radio_group = types.RadioGroup()

                for choice in classes:
                    class_radio_group.add_choice(choice, label=choice)

                inputs.enum(
                "class_radio_group",
                class_radio_group.values(),
                label="Choose Class",
                description="Choose what class to sort on:",
                view=types.DropdownView(),
                required=True,
                )

        inputs.bool(
        "reverse",
        label="Sort by reverse?",
        description="Sort from highest to lowest if on.",
        view=types.SwitchView(),
        )

    return True



def _sort_detections(ctx):
    sort_by = ctx.params.get("sort_radio_group")
    field = ctx.params.get("det_radio_group")
    by_class = ctx.params.get("sort_by_class")
    reverse = ctx.params.get("reverse")
    target = ctx.params.get("target", None)
    target_view = _get_target_view(ctx, target)
    if sort_by == "Number of Detections":
        if by_class:
            cls = ctx.params.get("class_radio_group")
            match = F("label").is_in((cls))
            sorted_box = target_view.match(
                F(field).filter(match).length() > 0
                ).sort_by(F(field).filter(match).length(),reverse=reverse)
            ctx.trigger("set_view", {"view": sorted_box._serialize()})
        else:
            sorted_box = target_view.sort_by(F(field).length(),reverse=reverse)
            ctx.trigger("set_view", {"view": sorted_box._serialize()})



    return



def _execution_mode(ctx, inputs):
    delegate = ctx.params.get("delegate", False)

    if delegate:
        description = "Uncheck this box to execute the operation immediately"
    else:
        description = "Check this box to delegate execution of this task"

    inputs.bool(
        "delegate",
        default=False,
        required=True,
        label="Delegate execution?",
        description=description,
        view=types.CheckboxView(),
    )

    if delegate:
        inputs.view(
            "notice",
            types.Notice(
                label=(
                    "You've chosen delegated execution. Note that you must "
                    "have a delegated operation service running in order for "
                    "this task to be processed. See "
                    "https://docs.voxel51.com/plugins/index.html#operators "
                    "for more information"
                )
            ),
        )



def get_target_view(ctx, inputs):
    has_view = ctx.view != ctx.dataset.view()
    has_selected = bool(ctx.selected)
    default_target = None

    if has_view or has_selected:
        target_choices = types.RadioGroup(orientation="horizontal")
        target_choices.add_choice(
            "DATASET",
            label="Entire dataset",
            description="Process the entire dataset",
        )

        if has_view:
            target_choices.add_choice(
                "CURRENT_VIEW",
                label="Current view",
                description="Process the current view",
            )
            default_target = "CURRENT_VIEW"

        if has_selected:
            target_choices.add_choice(
                "SELECTED_SAMPLES",
                label="Selected samples",
                description="Process only the selected samples",
            )
            default_target = "SELECTED_SAMPLES"

        inputs.enum(
            "target",
            target_choices.values(),
            default=default_target,
            required=True,
            label="Target view",
            view=target_choices,
        )

    target = ctx.params.get("target", default_target)

    return _get_target_view(ctx, target)

def _get_target_view(ctx, target):
    if target == "SELECTED_SAMPLES":
        return ctx.view.select(ctx.selected)

    if target == "DATASET":
        return ctx.dataset

    return ctx.view

def register(plugin):
    plugin.register(SortByDetections)
