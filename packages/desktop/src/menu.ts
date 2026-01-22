import { Menu, MenuItem, PredefinedMenuItem, Submenu } from "@tauri-apps/api/menu"
import { type as ostype } from "@tauri-apps/plugin-os"
import { getCurrentWindow } from "@tauri-apps/api/window"

import { runUpdater, UPDATER_ENABLED } from "./updater"

export async function createMenu() {
  if (ostype() !== "macos") return

  const menu = await Menu.new({
    items: [
      await Submenu.new({
        text: "OpenPatent",
        items: [
          await PredefinedMenuItem.new({
            item: { About: null },
          }),
          await MenuItem.new({
            enabled: UPDATER_ENABLED,
            action: () => runUpdater({ alertOnFail: true }),
            text: "Check For Updates...",
          }),
          await PredefinedMenuItem.new({
            item: "Separator",
          }),
          await MenuItem.new({
            action: async () => {
              await getCurrentWindow().emit("open-patent-hub")
            },
            text: "Patent Hub...",
          }),
          await PredefinedMenuItem.new({
            item: "Separator",
          }),
          await PredefinedMenuItem.new({
            item: "Hide",
          }),
          await PredefinedMenuItem.new({
            item: "HideOthers",
          }),
          await PredefinedMenuItem.new({
            item: "ShowAll",
          }),
          await PredefinedMenuItem.new({
            item: "Separator",
          }),
          await PredefinedMenuItem.new({
            item: "Quit",
          }),
        ].filter(Boolean),
      }),
      await Submenu.new({
        text: "Edit",
        items: [
          await PredefinedMenuItem.new({
            item: "Undo",
          }),
          await PredefinedMenuItem.new({
            item: "Redo",
          }),
          await PredefinedMenuItem.new({
            item: "Separator",
          }),
          await PredefinedMenuItem.new({
            item: "Cut",
          }),
          await PredefinedMenuItem.new({
            item: "Copy",
          }),
          await PredefinedMenuItem.new({
            item: "Paste",
          }),
          await PredefinedMenuItem.new({
            item: "SelectAll",
          }),
        ],
      }),
      await Submenu.new({
        text: "Settings",
        items: [
          await MenuItem.new({
            action: async () => {
              await getCurrentWindow().emit("open-settings")
            },
            text: "Open Settings...",
          }),
          await MenuItem.new({
            action: async () => {
              await getCurrentWindow().emit("open-agents")
            },
            text: "Agents...",
          }),
          await MenuItem.new({
            action: async () => {
              await getCurrentWindow().emit("open-premium")
            },
            text: "Premium...",
          }),
        ],
      }),
    ],
  })
  menu.setAsAppMenu()
}
