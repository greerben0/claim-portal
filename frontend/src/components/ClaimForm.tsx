import { useState } from "react";

import Form from "@cloudscape-design/components/form";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Button from "@cloudscape-design/components/button";
import Container from "@cloudscape-design/components/container";
import Header from "@cloudscape-design/components/header";
import FormField from "@cloudscape-design/components/form-field";
import FileUpload from "@cloudscape-design/components/file-upload";
import Multiselect from "@cloudscape-design/components/multiselect";
import Input from "@cloudscape-design/components/input";

import { createClaim } from "../utils/api";
import { fetchAuthSession } from '@aws-amplify/auth';


import type { MultiselectProps } from "@cloudscape-design/components/multiselect";

import tags from "../utils/defaultTagOptions";

const ENTER_KEY_CODE = 13;

interface ClaimFormProps {
    submitHandler: () => void;
}

const ClaimForm = ({ submitHandler }: ClaimFormProps) => {
    const [file, setFile] = useState<File[]>([]);
    const [selectedTags, setSelectedTags] = useState<MultiselectProps.Option[]>([]);
    const [client, setClient] = useState('');
    const [newTag, setNewTag] = useState('');
    const [errorText, setErrorText] = useState('')

    const handleSubmit = async () => {
        if (!file || file.length < 1) return;

        const selectedTagsStr = selectedTags.map(t => t.label || '')

        fetchAuthSession()
            .then((session) => {
                const accessToken = session.tokens?.accessToken?.toString()

                createClaim(accessToken || '', client, file[0], selectedTagsStr)
                    .then(() => submitHandler())
                    .then(() => clearInputs())
                    .catch(({ message }: { message: string }) => {
                        setErrorText(message)
                    })
            })
    }

    const clearInputs = async () => {
        setFile([])
        setSelectedTags([])
        setClient('')
        setNewTag('')
        setErrorText('')
    }

    const selectNewTag = async () => {
        if (newTag.length < 1)
            return;

        const newTagOption = {
            "label": newTag,
            "value": Math.random().toString(36).substring(2, 6) //unique value to satisfy MultiSelect requirement
        }
        tags.push(newTagOption)
        setSelectedTags(
            [
                ...selectedTags,
                newTagOption
            ])

        setNewTag('')
    }

    return (
        <Container>
            <form onSubmit={e => e.preventDefault()}>
                <Form
                    actions={
                        <SpaceBetween direction="horizontal" size="xs">
                            <Button formAction="none" variant="link" onClick={() => clearInputs()}>
                                Cancel
                            </Button>
                            <Button variant="primary" onClick={() => handleSubmit()}>Submit</Button>
                        </SpaceBetween>
                    }
                    header={<Header variant="h1">Create Claim</Header>}
                    errorText={errorText}
                >
                    <SpaceBetween direction="horizontal" size="xl">
                        <FormField label="Claim File" stretch>
                            <FileUpload
                                onChange={({ detail }) => setFile(detail.value)}
                                value={file}
                                multiple={false}
                                accept="txt"
                                showFileLastModified
                                tokenLimit={50}
                                constraintText="Text claim files only"
                            />
                        </FormField>
                        <FormField label="Client" stretch>
                            <Input
                                onChange={({ detail }) => setClient(detail.value)}
                                value={client}
                                placeholder="Enter Client Information"
                            />
                        </FormField>
                        <SpaceBetween size="s" direction="horizontal">
                            <FormField label="Select Tags">
                                <SpaceBetween size="s" direction="horizontal">
                                    <Input
                                        onChange={({ detail }) => setNewTag(detail.value)}
                                        value={newTag}
                                        onKeyDown={({ detail }) => {
                                            if (detail.keyCode == ENTER_KEY_CODE) {
                                                selectNewTag()
                                            }
                                        }}
                                        placeholder="Enter New Tag"
                                    />
                                    <Button iconName="add-plus" variant="icon" onClick={() => selectNewTag()} />
                                </SpaceBetween>

                                <Multiselect
                                    selectedOptions={selectedTags}
                                    onChange={({ detail }) => {
                                        setSelectedTags([...detail.selectedOptions])
                                    }}
                                    options={tags}
                                    filteringType="auto"
                                    placeholder="Select Existing Tags"
                                />
                            </FormField>


                        </SpaceBetween>

                    </SpaceBetween>
                </Form>

            </form>

        </Container>
    );
}

export default ClaimForm;

