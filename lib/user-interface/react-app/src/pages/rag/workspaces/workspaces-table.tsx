import {
  Alert,
  Pagination,
  PropertyFilter,
  Table,
} from "@cloudscape-design/components";
import { useCollection } from "@cloudscape-design/collection-hooks";
import { useCallback, useContext, useEffect, useState } from "react";
import { TextHelper } from "../../../common/helpers/text-helper";
import { TableEmptyState } from "../../../components/table-empty-state";
import { TableNoMatchState } from "../../../components/table-no-match-state";
import { WorkspacesPageHeader } from "./workspaces-page-header";
import { PropertyFilterI18nStrings } from "../../../common/i18n/property-filter-i18n-strings";
import {
  WorkspaceColumnFilteringProperties,
  WorkspacesColumnDefinitions,
} from "./column-definitions";
import { AppContext } from "../../../common/app-context";
import { ApiClient } from "../../../common/api-client/api-client";
import { Workspace } from "../../../API";
import { Utils } from "../../../common/utils";
import { UserContext } from "../../../common/user-context";
import { UserRole } from "../../../common/types";

export default function WorkspacesTable() {
  const appContext = useContext(AppContext);
  const userContext = useContext(UserContext)
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [globalError, setGlobalError] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const {
    items,
    actions,
    filteredItemsCount,
    collectionProps,
    paginationProps,
    propertyFilterProps,
  } = useCollection(workspaces, {
    propertyFiltering: {
      filteringProperties: WorkspaceColumnFilteringProperties,
      empty: (
        <TableEmptyState
          resourceName="Workspace"
          createHref={[UserRole.ADMIN, UserRole.WORKSPACES_MANAGER].includes(userContext.userRole) ? "/rag/workspaces/create" : undefined}
        />
      ),
      noMatch: (
        <TableNoMatchState
          onClearFilter={() => {
            actions.setPropertyFiltering({ tokens: [], operation: "and" });
          }}
        />
      ),
    },
    pagination: { pageSize: 50 },
    sorting: {
      defaultState: {
        sortingColumn: WorkspacesColumnDefinitions[4],
        isDescending: true,
      },
    },
    selection: {},
  });

  const getWorkspaces = useCallback(async () => {
    if (!appContext) return;

    const apiClient = new ApiClient(appContext);
    try {
      setGlobalError(undefined);
      const result = await apiClient.workspaces.getWorkspaces();

      setWorkspaces(result.data!.listWorkspaces);
    } catch (error) {
      console.error(Utils.getErrorMessage(error));
      setGlobalError(Utils.getErrorMessage(error));
    }

    setLoading(false);
  }, [appContext]);

  useEffect(() => {
    if (!appContext) return;

    getWorkspaces();
  }, [appContext, getWorkspaces]);

  return (
    <>
      {globalError && (
        <Alert
          statusIconAriaLabel="Error"
          type="error"
          header="Unable to load the workspaces."
        >
          {globalError}
        </Alert>
      )}
      <Table
        {...collectionProps}
        items={items}
        columnDefinitions={WorkspacesColumnDefinitions}
        selectionType="single"
        variant="full-page"
        stickyHeader={true}
        resizableColumns={true}
        header={
          <WorkspacesPageHeader
            selectedWorkspaces={collectionProps.selectedItems ?? []}
            getWorkspaces={getWorkspaces}
            counter={
              loading
                ? undefined
                : TextHelper.getHeaderCounterText(
                    workspaces,
                    collectionProps.selectedItems
                  )
            }
          />
        }
        loading={loading}
        loadingText="Loading Workspaces"
        filter={
          <PropertyFilter
            {...propertyFilterProps}
            i18nStrings={PropertyFilterI18nStrings}
            filteringPlaceholder={"Filter Workspaces"}
            countText={TextHelper.getTextFilterCounterText(filteredItemsCount)}
            expandToViewport={true}
          />
        }
        pagination={<Pagination {...paginationProps} />}
      />
    </>
  );
}
