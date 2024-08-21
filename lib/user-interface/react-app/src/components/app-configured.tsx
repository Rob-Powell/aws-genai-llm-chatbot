import { useCallback, useEffect, useState } from "react";
import {
  Authenticator,
  Heading,
  ThemeProvider,
  defaultDarkModeOverride,
  useTheme,
  Button,
  Divider,
  View,
} from "@aws-amplify/ui-react";
import App from "../app";
import { Amplify, Auth, Hub } from "aws-amplify";
import { AppConfig, UserRole } from "../common/types";
import { AppContext } from "../common/app-context";
import { UserContext, userContextDefault } from "../common/user-context";
import { Alert, StatusIndicator } from "@cloudscape-design/components";
import { StorageHelper } from "../common/helpers/storage-helper";
import { Mode } from "@cloudscape-design/global-styles";
import "@aws-amplify/ui-react/styles.css";
import { CHATBOT_NAME } from "../common/constants";

export default function AppConfigured() {
  const { tokens } = useTheme();
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [error, setError] = useState<boolean | null>(null);
  const [theme, setTheme] = useState(StorageHelper.getTheme());
  const [userRole, setUserRole] = useState(userContextDefault.userRole);
  const [userEmail, setUserEmail] = useState(userContextDefault.userEmail);

  const updateUserContext = useCallback(
    (event: string) => {
      if (event === "signIn" || event === "configured") {
        if (userRole === UserRole.UNDEFINED || userEmail === null) {
          Auth.currentAuthenticatedUser()
            .then((user) => {
              const userGroups = user.signInUserSession.idToken.payload['cognito:groups'] as string[] | undefined
              if (userGroups !== undefined && userGroups.length > 0) {
                // A user can be assigned multiple roles, both in and out of Chatbot scope
                // The following order of checking is based on permission scope to ensure the highest permission assigned is set
                if (userGroups.includes(UserRole.ADMIN)) {
                  setUserRole(UserRole.ADMIN);
                } else if (userGroups.includes(UserRole.WORKSPACES_MANAGER)) {
                  setUserRole(UserRole.WORKSPACES_MANAGER);
                } else if (userGroups.includes(UserRole.WORKSPACES_USER)) {
                  setUserRole(UserRole.WORKSPACES_USER);
                } else if (userGroups.includes(UserRole.CHATBOT_USER)) {
                  setUserRole(UserRole.CHATBOT_USER);
                } else {
                  setUserRole(UserRole.UNDEFINED);
                }
                if (user.attributes.email !== undefined) {
                  setUserEmail(user.attributes.email);
                }
              }
            })
            .catch(() => {
              setUserRole(UserRole.UNDEFINED);
            });
        }
      } else if (event === "signOut") {
        setUserRole(UserRole.UNDEFINED);
        setUserEmail("");
      }
    },
    [userRole, setUserRole, setUserEmail, userEmail]
  );

  useEffect(() => {
    (async () => {
      try {
        const result = await fetch("/aws-exports.json");
        const awsExports = await result.json();
        const currentConfig = Amplify.configure(awsExports) as AppConfig | null;

        // Extract the query string from the current URL
        const queryString = window.location.search;

        // Use URLSearchParams to work with the query string easily
        const urlParams = new URLSearchParams(queryString);

        if (
          currentConfig?.config.auth_federated_provider?.auto_redirect &&
          urlParams.get("loginlocal") != "true"
        ) {
          let authenticated = false;
          try {
            const user = await Auth.currentAuthenticatedUser();
            if (user) {
              authenticated = true;
            }
          } catch (e) {
            authenticated = false;
          }

          if (!authenticated) {
            const federatedProvider =
              currentConfig.config.auth_federated_provider;

            if (!federatedProvider.custom) {
              Auth.federatedSignIn({ provider: federatedProvider.name });
            } else {
              Auth.federatedSignIn({ customProvider: federatedProvider.name });
            }

            return;
          }
        }

        setConfig(currentConfig);
      } catch (e) {
        console.error(e);
        setError(true);
      }
    })();
  }, []);

  useEffect(() => {
    Hub.listen("auth", (authMessage) => {
      updateUserContext(authMessage.payload.event);
    });
  }, [updateUserContext]);

  useEffect(() => {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (
          mutation.type === "attributes" &&
          mutation.attributeName === "style"
        ) {
          const newValue =
            document.documentElement.style.getPropertyValue(
              "--app-color-scheme"
            );

          const mode = newValue === "dark" ? Mode.Dark : Mode.Light;
          if (mode !== theme) {
            setTheme(mode);
          }
        }
      });
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["style"],
    });

    return () => {
      observer.disconnect();
    };
  }, [theme]);

  if (!config) {
    if (error) {
      return (
        <div
          style={{
            height: "100%",
            width: "100%",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Alert header="Configuration error" type="error">
            Error loading configuration from "
            <a href="/aws-exports.json" style={{ fontWeight: "600" }}>
              /aws-exports.json
            </a>
            "
          </Alert>
        </div>
      );
    }

    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <StatusIndicator type="loading">Loading</StatusIndicator>
      </div>
    );
  }

  return (
    <AppContext.Provider value={config}>
      <UserContext.Provider
        value={{ setUserRole, userRole, setUserEmail, userEmail }}
      >
      <ThemeProvider
        theme={{
          name: "default-theme",
          overrides: [defaultDarkModeOverride],
        }}
        colorMode={theme === Mode.Dark ? "dark" : "light"}
      >
        <Authenticator
          hideSignUp={true}
          components={{
            SignIn: {
              Header: () => {
                if (config.config.auth_federated_provider) {
                  const signInWithCustomProvider = () => {
                    Auth.federatedSignIn({
                      customProvider:
                        config.config.auth_federated_provider?.name || "",
                    });
                  };
                  return (
                    <Heading
                      padding={`${tokens.space.xl} 0 0 ${tokens.space.xl}`}
                      level={3}
                    >
                      {CHATBOT_NAME}
                      <View as="div" paddingTop="1rem" paddingBottom="1rem">
                        <Button
                          onClick={signInWithCustomProvider}
                          variation="primary"
                        >
                          Sign in with{" "}
                          {config.config.auth_federated_provider?.name}
                        </Button>
                      </View>
                      <Divider label="OR" />
                    </Heading>
                  );
                } else {
                  return (
                    <Heading
                      padding={`${tokens.space.xl} 0 0 ${tokens.space.xl}`}
                      level={3}
                    >
                      {CHATBOT_NAME}
                    </Heading>
                  );
                }
              },
            },
          }}
        >
          <App />
        </Authenticator>
      </ThemeProvider>
      </UserContext.Provider>
    </AppContext.Provider>
  );
}
