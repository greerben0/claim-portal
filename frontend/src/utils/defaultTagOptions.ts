import type { MultiselectProps } from "@cloudscape-design/components/multiselect";

const tagLabels = [
    "auto",
    "home",
    "life",
    "urgent",
    "fire",
    "weather",
]

const tags: MultiselectProps.Option[] = tagLabels.map((label, idx) =>{ return {"label": label,"value": idx.toString()} })

export default tags