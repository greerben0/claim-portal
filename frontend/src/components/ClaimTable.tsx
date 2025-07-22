import Table from "@cloudscape-design/components/table";
import Box from "@cloudscape-design/components/box";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Header from "@cloudscape-design/components/header";
import Badge from "@cloudscape-design/components/badge";
import Button from "@cloudscape-design/components/button";

// import Pagination from "@cloudscape-design/components/pagination";

import type { ClaimItem } from "../types"

interface ClaimTableProps {
    claims: ClaimItem[]
    loading: boolean,
    triggerRefresh: () => void
}

export default function ClaimTable({ claims, loading, triggerRefresh }: ClaimTableProps) {
    // const [
    //     selectedItems,
    //     setSelectedItems
    // ] = React.useState<ClaimItem[]>([]);

    // const [currentPageIndex, setCurrentPageIndex] = React.useState(0)
    // const [pagesCount, setPagesCount] = React.useState(0)

    return (
        <Table
            renderAriaLive={({
                firstIndex,
                lastIndex,
                totalItemsCount
            }) =>
                `Displaying items ${firstIndex} to ${lastIndex} of ${totalItemsCount}`
            }

            // onSelectionChange={({ detail }) =>
            //     setSelectedItems(detail.selectedItems)
            // }
            // selectedItems={selectedItems}
            // selectionType="multi"

            ariaLabels={{
                selectionGroupLabel: "Items selection",
                allItemsSelectionLabel: () => "select all",
                // itemSelectionLabel: ({ selectedItems }, item: ClaimItem) =>
                //     item.claim_id
            }}

            columnDefinitions={[
                {
                    id: "claimId",
                    header: "Claim",
                    cell: item => item.claim_id,
                    sortingField: "claim_id",
                    isRowHeader: true
                },
                {
                    id: "client",
                    header: "Client",
                    cell: item => item.client,
                    sortingField: "client",
                    isRowHeader: true
                },
                {
                    id: "tags",
                    header: "Tags",
                    cell: item => {
                        return (
                            <SpaceBetween direction="horizontal" size="xs">
                                {
                                    item.tags.map(tag => (
                                        <Badge>{tag}</Badge>
                                    ))
                                }
                            </SpaceBetween>
                        )
                    }
                },
                {
                    id: "filename",
                    header: "Filename",
                    cell: item => item.filename,
                    sortingField: "filename"
                },
                {
                    id: "created_at",
                    header: "Created",
                    cell: item => item.created_at,
                    sortingField: "created_at"
                },
            ]}

            enableKeyboardNavigation

            items={claims}
            trackBy="claim_id"

            loadingText="Loading claims"
            loading={loading}

            empty={
                <Box
                    margin={{ vertical: "xs" }}
                    textAlign="center"
                    color="inherit"
                >
                    <SpaceBetween size="m">
                        <b>No Claims</b>
                    </SpaceBetween>
                </Box>
            }

            header={
                <Header
                    counter={
                        claims.length
                            ? "(" + claims.length + ")"
                            : ""
                    }
                    actions={<Button iconName="refresh" variant="icon" onClick={() => triggerRefresh()} />
}
                >
                    Claims
                </Header>
            }
        // pagination={
        //     <Pagination currentPageIndex={currentPageIndex} pagesCount={pagesCount} />
        // }
        />
    );
}