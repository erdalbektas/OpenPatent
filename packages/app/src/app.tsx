import "@/index.css"
import { ErrorBoundary, Show } from "solid-js"
import { Router, Route, Navigate } from "@solidjs/router"
import { MetaProvider } from "@solidjs/meta"
import { Font } from "@openpatent-ai/ui/font"
import { MarkedProvider } from "@openpatent-ai/ui/context/marked"
import { DiffComponentProvider } from "@openpatent-ai/ui/context/diff"
import { CodeComponentProvider } from "@openpatent-ai/ui/context/code"
import { Diff } from "@openpatent-ai/ui/diff"
import { Code } from "@openpatent-ai/ui/code"
import { ThemeProvider } from "@openpatent-ai/ui/theme"
import { GlobalSyncProvider } from "@/context/global-sync"
import { LayoutProvider } from "@/context/layout"
import { GlobalSDKProvider } from "@/context/global-sdk"
import { TerminalProvider } from "@/context/terminal"
import { PromptProvider } from "@/context/prompt"
import { NotificationProvider } from "@/context/notification"
import { DialogProvider } from "@openpatent-ai/ui/context/dialog"
import { CommandProvider } from "@/context/command"
import Layout from "@/pages/layout"
import Home from "@/pages/home"
import DirectoryLayout from "@/pages/directory-layout"
import Session from "@/pages/session"
import { ErrorPage } from "./pages/error"
import { iife } from "@openpatent-ai/util/iife"

declare global {
  interface Window {
    __openpatent__?: { updaterEnabled?: boolean; port?: number }
  }
}

const url = iife(() => {
  const param = new URLSearchParams(document.location.search).get("url")
  if (param) return param

  if (location.hostname.includes("openpatent.ai")) return "http://localhost:4096"
  if (window.__openpatent__) return `http://127.0.0.1:${window.__openpatent__.port}`
  if (import.meta.env.DEV)
    return `http://${import.meta.env.VITE_openpatent_SERVER_HOST ?? "localhost"}:${import.meta.env.VITE_openpatent_SERVER_PORT ?? "4096"}`

  return window.location.origin
})

export function App() {
  return (
    <MetaProvider>
      <Font />
      <ThemeProvider>
        <ErrorBoundary fallback={(error) => <ErrorPage error={error} />}>
          <DialogProvider>
            <MarkedProvider>
              <DiffComponentProvider component={Diff}>
                <CodeComponentProvider component={Code}>
                  <GlobalSDKProvider url={url}>
                    <GlobalSyncProvider>
                      <LayoutProvider>
                        <NotificationProvider>
                          <Router
                            root={(props) => (
                              <CommandProvider>
                                <Layout>{props.children}</Layout>
                              </CommandProvider>
                            )}
                          >
                            <Route path="/" component={Home} />
                            <Route path="/:dir" component={DirectoryLayout}>
                              <Route path="/" component={() => <Navigate href="session" />} />
                              <Route
                                path="/session/:id?"
                                component={(p) => (
                                  <Show when={p.params.id ?? "new"} keyed>
                                    <TerminalProvider>
                                      <PromptProvider>
                                        <Session />
                                      </PromptProvider>
                                    </TerminalProvider>
                                  </Show>
                                )}
                              />
                            </Route>
                          </Router>
                        </NotificationProvider>
                      </LayoutProvider>
                    </GlobalSyncProvider>
                  </GlobalSDKProvider>
                </CodeComponentProvider>
              </DiffComponentProvider>
            </MarkedProvider>
          </DialogProvider>
        </ErrorBoundary>
      </ThemeProvider>
    </MetaProvider>
  )
}
