#!/usr/bin/env python3
"""
Tkinter iPhone erase/restore assistant.
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from ..core.iphone_recovery import IPhoneDevice, IPhoneRecoveryManager


class IPhoneRecoveryWindow(tk.Toplevel):
    """Separate tool window for legitimate iPhone erase/restore."""

    APPLE_COMPUTER_RESET_URL = "https://support.apple.com/en-us/118430"
    APPLE_PASSCODE_RESET_URL = "https://support.apple.com/en-us/105039"

    def __init__(self, parent):
        super().__init__(parent)
        self.title("iPhone Erase Assistant")
        self.geometry("760x560")
        self.transient(parent)
        self.manager = IPhoneRecoveryManager()
        self.devices: list[IPhoneDevice] = []
        self.selected_device: IPhoneDevice | None = None
        self.restore_running = False
        self.auto_restore_armed = False

        self._build_widgets()
        self.scan_devices()

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        header = ttk.Frame(self, padding=(12, 10, 12, 4))
        header.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="iPhone Erase Assistant", font=("Arial", 13, "bold")).grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Label(
            header,
            text=(
                "For your own device only. This erases the phone, removes the passcode, "
                "and may still require the linked Apple Account during setup."
            ),
            wraplength=700,
        ).grid(row=1, column=0, sticky=tk.W, pady=(4, 0))

        tools = self.manager.tool_status()
        tool_text = (
            f"idevicerestore: {tools.idevicerestore or 'not installed'}\n"
            f"ideviceinfo: {tools.ideviceinfo or 'not installed'}\n"
            f"ideviceenterrecovery: {tools.ideviceenterrecovery or 'not installed'}\n"
            f"lsusb: {tools.lsusb or 'not installed'}"
        )
        ttk.Label(header, text=tool_text, font=("Courier", 9)).grid(row=2, column=0, sticky=tk.W, pady=(6, 0))

        actions = ttk.Frame(self, padding=(12, 4))
        actions.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.scan_button = ttk.Button(actions, text="Scan iPhone", command=self.scan_devices)
        self.scan_button.pack(side=tk.LEFT)
        self.restore_button = ttk.Button(
            actions,
            text="Erase and Restore Latest iOS",
            command=self.confirm_restore,
            state="disabled",
        )
        self.restore_button.pack(side=tk.LEFT, padx=(8, 0))
        self.auto_restore_button = ttk.Button(
            actions,
            text="Auto Restore When Plugged In",
            command=self.confirm_auto_restore,
        )
        self.auto_restore_button.pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Apple Reset Instructions", command=self.open_apple_reset).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(actions, text="Previous Passcode Help", command=self.open_passcode_reset).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        columns = ("Mode", "Product ID", "Description", "Serial")
        self.device_tree = ttk.Treeview(self, columns=columns, show="headings", height=5)
        for column in columns:
            self.device_tree.heading(column, text=column)
        self.device_tree.column("Mode", width=100)
        self.device_tree.column("Product ID", width=90)
        self.device_tree.column("Description", width=260)
        self.device_tree.column("Serial", width=250)
        self.device_tree.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=12, pady=(4, 8))
        self.device_tree.bind("<<TreeviewSelect>>", self.on_device_select)

        output_frame = ttk.LabelFrame(self, text="Status", padding=8)
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=12, pady=(0, 12))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output = tk.Text(output_frame, wrap=tk.WORD, height=14, font=("Courier", 9))
        self.output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.output.configure(yscrollcommand=scrollbar.set)

        self.write_status(
            "Before erasing, wait for the lockout timer if you still know the correct passcode.\n"
            "If you recently changed the passcode, try Apple's Previous Passcode option first.\n"
            "To restore by computer, put the iPhone on the recovery screen, then scan here."
        )

    def scan_devices(self):
        self.scan_button.configure(state="disabled")
        self.write_status("Scanning for Apple USB devices...")

        def worker():
            devices = self.manager.scan_devices()
            self.after(0, lambda: self.update_devices(devices))

        threading.Thread(target=worker, daemon=True).start()

    def update_devices(self, devices: list[IPhoneDevice]):
        self.devices = devices
        self.selected_device = None
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)

        for index, device in enumerate(devices):
            self.device_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(device.mode, device.product_id, device.description, device.serial),
            )

        self.scan_button.configure(state="normal")
        self.restore_button.configure(state="disabled")
        if devices:
            self.write_status(f"Found {len(devices)} Apple device(s). Select a recovery or DFU mode device to restore.")
        else:
            self.write_status("No Apple USB device found. Put the iPhone in recovery mode and connect it by USB.")

    def on_device_select(self, _event):
        selection = self.device_tree.selection()
        if not selection:
            self.selected_device = None
            self.restore_button.configure(state="disabled")
            return

        self.selected_device = self.devices[int(selection[0])]
        can_restore_mode = self.selected_device.mode in {"recovery", "dfu", "apple_usb"}
        can_restore = self.manager.tool_status().can_restore and can_restore_mode
        self.restore_button.configure(state="normal" if can_restore else "disabled")
        if not can_restore_mode:
            self.write_status("Selected device is in normal mode. Put it in recovery mode before erase/restore.")

    def confirm_restore(self):
        if not self.selected_device or self.restore_running:
            return

        warning = (
            "This will erase all data on the selected iPhone and install the latest signed iOS firmware.\n\n"
            "It does not bypass Activation Lock. You may need the Apple Account linked to this iPhone "
            "after restore.\n\n"
            "Continue?"
        )
        if not messagebox.askyesno("Erase iPhone", warning):
            return

        self.restore_running = True
        self.restore_button.configure(state="disabled")
        self.scan_button.configure(state="disabled")
        command = " ".join(self.manager.build_restore_command(self.selected_device))
        self.write_status(f"Starting restore command:\n{command}")

        def worker():
            try:
                code = self.manager.restore_latest_firmware(self.selected_device, self.write_status_threadsafe)
                self.after(0, lambda: self.restore_finished(code))
            except Exception as exc:
                self.after(0, lambda err=exc: self.restore_failed(str(err)))

        threading.Thread(target=worker, daemon=True).start()

    def confirm_auto_restore(self):
        if self.restore_running or self.auto_restore_armed:
            return

        tools = self.manager.tool_status()
        if not tools.can_restore:
            messagebox.showerror(
                "Restore Tool Missing",
                "idevicerestore is not installed. Install libimobiledevice/idevicerestore first.",
            )
            return

        warning = (
            "This will wait for an iPhone in recovery or DFU mode, then automatically erase it "
            "and install the latest signed iOS firmware.\n\n"
            "It does not bypass Activation Lock. You may need the Apple Account linked to this "
            "iPhone after restore.\n\n"
            "Continue?"
        )
        if not messagebox.askyesno("Auto Restore iPhone", warning):
            return

        self.restore_running = True
        self.auto_restore_armed = True
        self.restore_button.configure(state="disabled")
        self.scan_button.configure(state="disabled")
        self.auto_restore_button.configure(state="disabled")
        self.write_status("Auto restore armed. Put the iPhone in recovery or DFU mode and plug it in.")

        def worker():
            try:
                code = self.manager.auto_restore_when_connected(
                    timeout_seconds=None,
                    poll_interval=2.0,
                    output_callback=self.write_status_threadsafe,
                )
                self.after(0, lambda: self.restore_finished(code))
            except Exception as exc:
                self.after(0, lambda err=exc: self.restore_failed(str(err)))

        threading.Thread(target=worker, daemon=True).start()

    def restore_finished(self, code: int):
        self.restore_running = False
        self.auto_restore_armed = False
        self.scan_button.configure(state="normal")
        self.auto_restore_button.configure(state="normal")
        self.restore_button.configure(state="normal" if self.selected_device else "disabled")
        if code == 0:
            self.write_status("Restore completed. Set up the iPhone from the Hello screen.")
            messagebox.showinfo("Restore Complete", "The restore completed. Set up the iPhone from the Hello screen.")
        else:
            self.write_status(f"Restore exited with code {code}. Check the log above and Apple's reset instructions.")
            messagebox.showwarning("Restore Failed", f"Restore exited with code {code}.")

    def restore_failed(self, message: str):
        self.restore_running = False
        self.auto_restore_armed = False
        self.scan_button.configure(state="normal")
        self.auto_restore_button.configure(state="normal")
        self.restore_button.configure(state="normal" if self.selected_device else "disabled")
        self.write_status(f"Restore failed: {message}")
        messagebox.showerror("Restore Failed", message)

    def write_status_threadsafe(self, text: str):
        self.after(0, lambda: self.write_status(text))

    def write_status(self, text: str):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def open_apple_reset(self):
        webbrowser.open(self.APPLE_COMPUTER_RESET_URL)

    def open_passcode_reset(self):
        webbrowser.open(self.APPLE_PASSCODE_RESET_URL)
