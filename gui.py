import tkinter as tk
from tkinter import filedialog, messagebox
import os
from backend import (
    load_groups, save_groups, authenticate_google, get_connected_email,
    get_calendar_events, read_csv_tasks, analyze_tasks_with_ai, send_email, logout
)


class TaskReporterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Task Report Manager')
        self.geometry('1000x720')
        self.resizable(False, False)

        self.gmail_service = None
        self.calendar_service = None
        self.groups = load_groups()
        self.selected_group_index = None

        self.connected_email = tk.StringVar(value='Not connected')
        self.source_var = tk.StringVar(value='calendar')
        self.csv_path_var = tk.StringVar()
        self.group_title_var = tk.StringVar()
        self.group_description_var = tk.StringVar()

        self.create_widgets()
        self.connect_google()

    def create_widgets(self):
        header_frame = tk.Frame(self, pady=10, bg='#f0f0f0')
        header_frame.pack(fill='x')

        tk.Label(header_frame, text='Task Report Manager', font=('Segoe UI', 18, 'bold'), bg='#f0f0f0').pack(side='left', padx=20)
        
        auth_frame = tk.Frame(header_frame, bg='#f0f0f0')
        auth_frame.pack(side='right', padx=20)
        
        tk.Label(auth_frame, textvariable=self.connected_email, font=('Segoe UI', 10), fg='#0078d4', bg='#f0f0f0').pack(side='left', padx=(0, 10))
        tk.Button(auth_frame, text='Login', width=8, command=self.login_account).pack(side='left', padx=2)
        tk.Button(auth_frame, text='Logout', width=8, command=self.logout_account).pack(side='left', padx=2)

        content_frame = tk.Frame(self)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        left_frame = tk.Frame(content_frame, bd=1, relief='solid', width=300)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text='Recipient Groups', font=('Segoe UI', 12, 'bold')).pack(pady=10)
        self.group_listbox = tk.Listbox(left_frame, width=40, height=24)
        self.group_listbox.pack(padx=10, pady=(0, 10))
        self.group_listbox.bind('<<ListboxSelect>>', self.on_group_select)

        group_button_frame = tk.Frame(left_frame)
        group_button_frame.pack(pady=10)
        tk.Button(group_button_frame, text='New Group', width=12, command=self.clear_group_form).grid(row=0, column=0, padx=4)
        tk.Button(group_button_frame, text='Save Group', width=12, command=self.save_group).grid(row=0, column=1, padx=4)
        tk.Button(group_button_frame, text='Delete Group', width=12, command=self.delete_group).grid(row=1, column=0, columnspan=2, pady=6)

        right_frame = tk.Frame(content_frame, bd=1, relief='solid')
        right_frame.pack(side='left', fill='both', expand=True)

        form_frame = tk.Frame(right_frame, padx=20, pady=20)
        form_frame.pack(fill='x')

        tk.Label(form_frame, text='Group Title', font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w')
        tk.Entry(form_frame, textvariable=self.group_title_var, width=60).grid(row=1, column=0, sticky='w', pady=(0, 10))

        tk.Label(form_frame, text='Description', font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w')
        tk.Entry(form_frame, textvariable=self.group_description_var, width=60).grid(row=3, column=0, sticky='w', pady=(0, 10))

        tk.Label(form_frame, text='Recipients (one email per line)', font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky='w')
        self.recipients_text = tk.Text(form_frame, width=70, height=8)
        self.recipients_text.grid(row=5, column=0, sticky='w', pady=(0, 10))

        source_frame = tk.LabelFrame(right_frame, text='Report Source', padx=12, pady=10)
        source_frame.pack(fill='x', padx=20, pady=(0, 10))

        tk.Radiobutton(source_frame, text='Google Calendar', variable=self.source_var, value='calendar').grid(row=0, column=0, sticky='w', padx=4, pady=2)
        tk.Radiobutton(source_frame, text='CSV File', variable=self.source_var, value='csv').grid(row=1, column=0, sticky='w', padx=4, pady=2)

        csv_frame = tk.Frame(source_frame)
        csv_frame.grid(row=2, column=0, sticky='w', pady=(6, 0))
        tk.Entry(csv_frame, textvariable=self.csv_path_var, width=50).grid(row=0, column=0, padx=(0, 8))
        tk.Button(csv_frame, text='Browse', command=self.pick_csv_file).grid(row=0, column=1)

        action_frame = tk.Frame(right_frame, pady=10)
        action_frame.pack(fill='x', padx=20)
        tk.Button(action_frame, text='Generate Report', width=18, command=self.generate_report).grid(row=0, column=0, padx=6)
        tk.Button(action_frame, text='Send Report', width=18, command=self.send_report).grid(row=0, column=1, padx=6)

        preview_frame = tk.Frame(right_frame, bd=1, relief='solid', padx=10, pady=10)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        tk.Label(preview_frame, text='Report Preview', font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        self.report_text = tk.Text(preview_frame, wrap='word', height=16)
        self.report_text.pack(fill='both', expand=True, pady=(6, 0))

        self.refresh_groups()

    def connect_google(self):
        try:
            self.gmail_service, self.calendar_service = authenticate_google()
            connected = get_connected_email(self.gmail_service)
            self.connected_email.set(f'Connected: {connected}')
        except Exception as exc:
            self.connected_email.set('Not connected')
            messagebox.showwarning('Google Authentication', f'Google login is required for sending reports.\n{exc}')

    def login_account(self):
        """Explicitly login to Google account."""
        try:
            self.gmail_service, self.calendar_service = authenticate_google()
            connected = get_connected_email(self.gmail_service)
            self.connected_email.set(f'Connected: {connected}')
            messagebox.showinfo('Login Successful', f'Logged in as: {connected}')
        except Exception as exc:
            self.connected_email.set('Not connected')
            messagebox.showerror('Login Failed', f'Failed to authenticate:\n{exc}')

    def logout_account(self):
        """Logout from Google account."""
        if logout():
            self.gmail_service = None
            self.calendar_service = None
            self.connected_email.set('Not connected')
            messagebox.showinfo('Logout Successful', 'You have been logged out.')
        else:
            messagebox.showinfo('Logout', 'No active session to logout from.')

    def refresh_groups(self):
        self.group_listbox.delete(0, tk.END)
        for group in self.groups:
            self.group_listbox.insert(tk.END, group.get('title', 'Untitled Group'))

    def on_group_select(self, event):
        selection = self.group_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        self.selected_group_index = index
        group = self.groups[index]
        self.group_title_var.set(group.get('title', ''))
        self.group_description_var.set(group.get('description', ''))
        self.recipients_text.delete('1.0', tk.END)
        self.recipients_text.insert(tk.END, '\n'.join(group.get('recipients', [])))

    def clear_group_form(self):
        self.selected_group_index = None
        self.group_title_var.set('')
        self.group_description_var.set('')
        self.recipients_text.delete('1.0', tk.END)
        self.group_listbox.selection_clear(0, tk.END)

    def save_group(self):
        title = self.group_title_var.get().strip()
        description = self.group_description_var.get().strip()
        recipients = [line.strip() for line in self.recipients_text.get('1.0', tk.END).splitlines() if line.strip()]

        if not title:
            messagebox.showerror('Validation Error', 'Group title is required.')
            return
        if not recipients:
            messagebox.showerror('Validation Error', 'At least one recipient email is required.')
            return

        group = {
            'title': title,
            'description': description,
            'recipients': recipients
        }

        if self.selected_group_index is not None:
            self.groups[self.selected_group_index] = group
        else:
            self.groups.append(group)
            self.selected_group_index = len(self.groups) - 1

        save_groups(self.groups)
        self.refresh_groups()
        self.group_listbox.select_set(self.selected_group_index)
        messagebox.showinfo('Saved', 'Recipient group saved successfully.')

    def delete_group(self):
        selection = self.group_listbox.curselection()
        if not selection:
            messagebox.showwarning('Delete Group', 'Select a group first.')
            return
        index = selection[0]
        group = self.groups.pop(index)
        save_groups(self.groups)
        self.refresh_groups()
        self.clear_group_form()
        messagebox.showinfo('Deleted', f'Recipient group "{group.get("title", "Untitled Group")}" deleted.')

    def pick_csv_file(self):
        path = filedialog.askopenfilename(
            title='Select CSV file',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')]
        )
        if path:
            self.csv_path_var.set(path)

    def generate_report(self):
        if self.source_var.get() == 'calendar':
            if not self.calendar_service:
                self.connect_google()
                if not self.calendar_service:
                    return
            events = get_calendar_events(self.calendar_service)
            tasks_data = '\n'.join([
                f"{event.get('summary', 'No title')} at {event['start'].get('dateTime', event['start'].get('date', 'Unknown'))}"
                for event in events
            ])
            source = 'calendar events'
        else:
            csv_path = self.csv_path_var.get().strip()
            if not csv_path or not os.path.exists(csv_path):
                messagebox.showerror('CSV Error', 'Please choose a valid CSV file path.')
                return
            tasks = read_csv_tasks(csv_path)
            tasks_data = '\n'.join([str(task) for task in tasks])
            source = 'CSV tasks'

        if not tasks_data:
            tasks_data = 'No items found.'

        report = analyze_tasks_with_ai(tasks_data, source)
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert(tk.END, report)

    def send_report(self):
        report = self.report_text.get('1.0', tk.END).strip()
        if not report:
            messagebox.showwarning('No Report', 'Generate a report before sending.')
            return

        recipients = [line.strip() for line in self.recipients_text.get('1.0', tk.END).splitlines() if line.strip()]
        if not recipients:
            messagebox.showwarning('No Recipients', 'Add at least one recipient email.')
            return

        if not self.gmail_service:
            self.connect_google()
            if not self.gmail_service:
                return

        subject = 'Automated Task Report'
        sent_to = []
        errors = []
        for email in recipients:
            try:
                message_id = send_email(self.gmail_service, email, subject, report)
                sent_to.append((email, message_id))
            except Exception as exc:
                errors.append(f'{email}: {exc}')

        summary = f'Sent to {len(sent_to)} recipient(s).' if sent_to else 'No emails were sent.'
        if errors:
            summary += '\nErrors:\n' + '\n'.join(errors)

        messagebox.showinfo('Send Report', summary)