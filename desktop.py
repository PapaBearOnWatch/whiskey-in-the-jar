import customtkinter as ctk
from PIL import Image
import tkinter as tk
import tempfile
import atexit
import shutil
import msvcrt
from tkinter import filedialog, messagebox
from pathlib import Path
from email import policy
from email.parser import BytesParser

from tkinterdnd2 import TkinterDnD, DND_FILES

from collector.email_ingest import ingest_email
from analyzer.email_analyzer import analyze_email
from database.init_db import initialize_database, get_connection


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class WhiskeyApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Whiskey in the Jar | Email Intelligence")
        self.geometry("1100x850")
        self.minsize(900, 700)

        self.selected_file = None
        self.email_bytes = None

        self.configure(fg_color="#14251D")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_welcome_screen()

    def build_welcome_screen(self):
        self.welcome_frame = ctk.CTkFrame(
            self,
            fg_color="#14251D",
            corner_radius=0
        )
        self.welcome_frame.grid(
            row=0, column=0, sticky="nsew", padx=20, pady=20
        )
        self.welcome_frame.grid_columnconfigure(0, weight=1)

        image_path = Path(__file__).parent / "assets" / "whiskey_welcome.png"

        try:
            original = Image.open(image_path)
            original.thumbnail((1000, 600), Image.Resampling.LANCZOS)

            self.welcome_image = ctk.CTkImage(
                light_image=original,
                dark_image=original,
                size=original.size
            )

            ctk.CTkLabel(
                self.welcome_frame,
                text="",
                image=self.welcome_image
            ).grid(row=0, column=0, pady=(10, 15))

        except Exception as error:
            ctk.CTkLabel(
                self.welcome_frame,
                text="WHISKEY IN THE JAR",
                text_color="#D6B66B",
                font=("Arial", 30, "bold")
            ).grid(row=0, column=0, pady=40)

        ctk.CTkLabel(
            self.welcome_frame,
            text="DEMONSTRATION BUILD",
            text_color="#D6B66B",
            font=("Arial", 13, "bold")
        ).grid(row=1, column=0, pady=(5, 5))

        ctk.CTkLabel(
            self.welcome_frame,
            text="A functional preview for evaluation and in-person demonstrations. Emails are analyzed on this computer.",
            text_color="#E8E2D5",
            font=("Arial", 12),
            wraplength=750
        ).grid(row=2, column=0, padx=30, pady=(0, 20))

        ctk.CTkButton(
            self.welcome_frame,
            text="PROCEED TO WHISKEY",
            command=self.proceed_to_whiskey,
            fg_color="#B99A52",
            hover_color="#96783A",
            text_color="#14251D",
            font=("Arial", 14, "bold"),
            height=45,
            width=260
        ).grid(row=3, column=0, pady=(5, 20))

    def proceed_to_whiskey(self):
        self.welcome_frame.destroy()

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=1)

        self.build_header()
        self.build_input_area()
        self.build_results_area()
        self.build_footer()
    def build_header(self):
        header = ctk.CTkFrame(
            self, fg_color="#1D382B", corner_radius=12
        )
        header.grid(
            row=0, column=0, padx=25, pady=(20, 10), sticky="ew"
        )

        ctk.CTkLabel(
            header,
            text="WHISKEY IN THE JAR",
            font=("Georgia", 30, "bold"),
            text_color="#D6B66B"
        ).pack(pady=(15, 3))

        ctk.CTkLabel(
            header,
            text="CYBERSECURITY. NO CHASER.",
            font=("Arial", 12),
            text_color="#D6D0BD"
        ).pack(pady=(0, 15))

    def build_input_area(self):
        area = ctk.CTkFrame(
            self, fg_color="#1D382B", corner_radius=12
        )
        area.grid(
            row=1, column=0, padx=25, pady=10, sticky="ew"
        )

        ctk.CTkLabel(
            area,
            text="BRING AN EMAIL TO THE TABLE",
            font=("Arial", 16, "bold"),
            text_color="#D6B66B"
        ).pack(pady=(15, 8))

        self.drop_label = ctk.CTkLabel(
            area,
            text="DROP AN .EML FILE HERE",
            height=65,
            fg_color="#294735",
            corner_radius=10,
            text_color="#F0EBDD",
            font=("Arial", 15, "bold")
        )
        self.drop_label.pack(fill="x", padx=20, pady=8)

        self.drop_label.drop_target_register(
            DND_FILES
        )
        self.drop_label.dnd_bind(
            "<<Drop>>", self.handle_drop
        )

        ctk.CTkButton(
            area,
            text="BROWSE FOR EMAIL",
            command=self.select_email,
            fg_color="#A88643",
            hover_color="#896B35",
            text_color="#14251D"
        ).pack(pady=8)

        ctk.CTkLabel(
            area,
            text="OR PASTE THE ORIGINAL EMAIL SOURCE",
            text_color="#D6D0BD",
            font=("Arial", 12, "bold")
        ).pack(pady=(10, 5))

        self.paste_box = ctk.CTkTextbox(
            area,
            height=110,
            fg_color="#F0EBDD",
            text_color="#26352B",
            font=("Consolas", 11),
            wrap="word"
        )
        self.paste_box.pack(fill="x", padx=20, pady=5)
        self.paste_box.bind("<Button-3>", self.show_text_context_menu)

        self.paste_box.insert(
            "1.0",
            "Paste email source here..."
        )

        self.paste_box._textbox.bind("<FocusIn>", self.clear_placeholder, add="+")

        self.status_label = ctk.CTkLabel(
            area,
            text="No email loaded",
            text_color="#D6D0BD"
        )
        self.status_label.pack(pady=5)

        ctk.CTkButton(
            area,
            text="ANALYZE EMAIL",
            command=self.run_analysis,
            fg_color="#A88643",
            hover_color="#896B35",
            text_color="#14251D"
        ).pack(pady=(5, 15))


    def show_text_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="Cut",
            command=lambda: self.paste_box._textbox.event_generate("<<Cut>>")
        )
        menu.add_command(
            label="Copy",
            command=lambda: self.paste_box._textbox.event_generate("<<Copy>>")
        )
        menu.add_command(
            label="Paste",
            command=lambda: self.paste_box._textbox.event_generate("<<Paste>>")
        )
        menu.add_separator()
        menu.add_command(
            label="Select All",
            command=lambda: self.paste_box._textbox.tag_add(
                "sel", "1.0", "end-1c"
            )
        )

        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()
        return "break"
    def reset_paste_box(self):
        self.paste_box.delete("1.0", "end")
        self.paste_box.insert("1.0", "Paste email source here...")
        self.email_bytes = None
        self.selected_file = None
    def clear_placeholder(self, event=None):
        if self.paste_box.get("1.0", "end").strip() == "Paste email source here...":
            self.paste_box.delete("1.0", "end")

    def select_email(self):
        filename = filedialog.askopenfilename(
            title="Select an email",
            filetypes=[("Email files", "*.eml"), ("All files", "*.*")]
        )
        if filename:
            self.load_file(Path(filename))

    def load_file(self, path):
        try:
            if path.suffix.lower() != ".eml":
                messagebox.showwarning(
                    "Unsupported file",
                    "Please select an .eml email file."
                )
                return

            if not path.is_file():
                return

            if path.stat().st_size > 10 * 1024 * 1024:
                messagebox.showerror(
                    "File too large",
                    "Email files must be 10 MB or smaller."
                )
                return

            self.email_bytes = path.read_bytes()
            self.selected_file = path
            self.paste_box.delete("1.0", "end")
            self.status_label.configure(
                text=f"Email ready: {path.name}"
            )

        except OSError as error:
            messagebox.showerror("File Error", str(error))

    def handle_drop(self, event):
        try:
            files = self.tk.splitlist(event.data)
            if files:
                self.load_file(Path(files[0]))
        except Exception as error:
            messagebox.showerror("Drop Error", str(error))

        return "copy"

    def run_analysis(self):
        try:
            pasted_text = self.paste_box.get("1.0", "end").strip()

            if pasted_text and pasted_text != "Paste email source here...":
                raw_email = pasted_text.encode("utf-8")
                source_name = "Pasted email"
            elif self.email_bytes:
                raw_email = self.email_bytes
                source_name = self.selected_file.name
            else:
                messagebox.showinfo(
                    "No Email",
                    "Please drop, select, or paste an email first."
                )
                return

            if not raw_email.strip():
                raise ValueError("The email is empty.")

            ingestion = ingest_email(raw_email)
            email_id = ingestion["email_id"]

            result = analyze_email(email_id)

            with get_connection() as connection:
                email = connection.execute(
                    "SELECT sender, recipient, subject "
                    "FROM emails WHERE id = ?",
                    (email_id,)
                ).fetchone()

            self.show_analysis(result, email, source_name)
            self.status_label.configure(
                text=f"Analysis complete: {source_name}"
            )

            self.reset_paste_box()
            self.status_label.configure(text="Ready for next email")

        except Exception as error:
            messagebox.showerror("Analysis Error", str(error))

    def show_results(self, text):
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", text)
        self.results.configure(state="disabled")

    def build_results_area(self):
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#F0EBDD",
            corner_radius=12
        )
        self.results_frame.grid(
            row=2, column=0, padx=25, pady=10, sticky="nsew"
        )
        self.results_frame.grid_columnconfigure(0, weight=1)

        self.show_welcome()

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_results()

        ctk.CTkLabel(
            self.results_frame,
            text="WELCOME TO WHISKEY IN THE JAR",
            font=("Georgia", 23, "bold"),
            text_color="#26352B"
        ).pack(pady=(35, 15))

        ctk.CTkLabel(
            self.results_frame,
            text="A closer look at the emails in your inbox.",
            font=("Arial", 16),
            text_color="#59675C"
        ).pack(pady=5)

        ctk.CTkLabel(
            self.results_frame,
            text=(
                "Select, drop, or paste an email to begin.\n\n"
                "Whiskey examines indicators that may suggest "
                "suspicious activity. It does not establish "
                "whether an email is definitively malicious."
            ),
            font=("Arial", 14),
            text_color="#26352B",
            justify="center",
            wraplength=750
        ).pack(pady=25)




    def show_analysis(self, result, email, source_name):
        self.clear_results()

        risk = result["risk_level"].upper()

        risk_styles = {
            "HIGH": ("#8F3832", "Potentially dangerous indicators were found."),
            "MEDIUM": ("#A88643", "Some indicators deserve a closer look."),
            "LOW": ("#416B4C", "No suspicious indicators were detected by current rules.")
        }

        risk_color, risk_message = risk_styles.get(
            risk, ("#59675C", "Assessment completed.")
        )

        ctk.CTkLabel(
            self.results_frame,
            text="EMAIL SECURITY ASSESSMENT",
            font=("Georgia", 23, "bold"),
            text_color="#26352B"
        ).pack(anchor="w", padx=25, pady=(22, 8))

        summary = ctk.CTkFrame(
            self.results_frame,
            fg_color=risk_color,
            corner_radius=12
        )
        summary.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            summary,
            text=f"{risk} RISK",
            font=("Arial", 25, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 3))

        ctk.CTkLabel(
            summary,
            text=risk_message,
            font=("Arial", 14),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        details = ctk.CTkFrame(
            self.results_frame,
            fg_color="#E4DFCE",
            corner_radius=10
        )
        details.pack(fill="x", padx=20, pady=8)

        for label, value in [
            ("Subject", email["subject"] or "Not provided"),
            ("Sender", email["sender"] or "Not provided"),
            ("Source", source_name),
            ("Indicator score", str(result["score"])),
            ("URLs found", str(result["url_count"]))
        ]:
            row = ctk.CTkFrame(details, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)

            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=("Arial", 12, "bold"),
                text_color="#26352B"
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=("Arial", 12),
                text_color="#26352B",
                wraplength=550
            ).pack(side="left", padx=8)

        ctk.CTkLabel(
            self.results_frame,
            text="WHAT WHISKEY NOTICED",
            font=("Arial", 17, "bold"),
            text_color="#896B35"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        explanations = {
            "urgency_language": (
                "Urgent language",
                "Messages that pressure you to act quickly can discourage "
                "you from checking whether a request is legitimate."
            ),
            "possible_impersonation": (
                "Possible brand impersonation",
                "The sender's displayed identity may be imitating a known "
                "organization. Check the actual sender address carefully."
            ),
            "unencrypted_url": (
                "Unencrypted web link",
                "This link uses HTTP rather than HTTPS. Information sent "
                "through it may not be protected in transit."
            )
        }

        if result["findings"]:
            for finding in result["findings"]:
                finding_type = finding["type"]
                title, explanation = explanations.get(
                    finding_type,
                    (
                        finding_type.replace("_", " ").title(),
                        "Whiskey detected an indicator that deserves review."
                    )
                )

                card = ctk.CTkFrame(
                    self.results_frame,
                    fg_color="#FFFFFF",
                    corner_radius=10,
                    border_width=1,
                    border_color="#D6D0BD"
                )
                card.pack(fill="x", padx=20, pady=6)

                ctk.CTkLabel(
                    card,
                    text=title,
                    font=("Arial", 14, "bold"),
                    text_color="#26352B"
                ).pack(anchor="w", padx=15, pady=(12, 3))

                ctk.CTkLabel(
                    card,
                    text=explanation,
                    font=("Arial", 12),
                    text_color="#59675C",
                    wraplength=750,
                    justify="left"
                ).pack(anchor="w", padx=15, pady=3)

                ctk.CTkLabel(
                    card,
                    text=f"Technical finding: {finding['description']}",
                    font=("Arial", 11),
                    text_color="#896B35",
                    wraplength=750,
                    justify="left"
                ).pack(anchor="w", padx=15, pady=(3, 12))
        else:
            ctk.CTkLabel(
                self.results_frame,
                text="No suspicious indicators were detected by the current rules.",
                font=("Arial", 13),
                text_color="#26352B",
                wraplength=750
            ).pack(anchor="w", padx=25, pady=12)

        ctk.CTkLabel(
            self.results_frame,
            text="WHAT SHOULD I DO?",
            font=("Arial", 17, "bold"),
            text_color="#896B35"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        if risk == "HIGH":
            advice = (
                "Do not click links or open attachments in this message. "
                "Do not reply with personal or financial information. "
                "If it claims to come from an organization you use, "
                "contact that organization through a website or phone "
                "number you already know is genuine."
            )
        elif risk == "MEDIUM":
            advice = (
                "Pause before responding. Check the sender address and "
                "verify unexpected requests through a separate, trusted "
                "contact method. Avoid clicking unfamiliar links."
            )
        else:
            advice = (
                "No warning signs were detected by the current rules. "
                "That does not guarantee the message is safe. Be cautious "
                "with unexpected requests, links, and attachments."
            )

        advice_card = ctk.CTkFrame(
            self.results_frame,
            fg_color="#E4DFCE",
            corner_radius=10
        )
        advice_card.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(
            advice_card,
            text=advice,
            font=("Arial", 13),
            text_color="#26352B",
            wraplength=750,
            justify="left"
        ).pack(anchor="w", padx=18, pady=15)

        technical = ctk.CTkFrame(
            self.results_frame,
            fg_color="#E4DFCE",
            corner_radius=10
        )
        technical.pack(fill="x", padx=20, pady=(12, 20))

        technical_button = ctk.CTkButton(
            technical,
            text="SHOW TECHNICAL DETAILS",
            fg_color="#294735",
            hover_color="#1D382B",
            command=lambda: self.toggle_technical(technical)
        )
        technical_button.pack(anchor="w", padx=12, pady=10)

        technical_content = ctk.CTkFrame(
            technical,
            fg_color="transparent"
        )

        technical_lines = [
            f"Assessment: {result['assessment']}",
            "",
            "Extracted indicators:"
        ]

        for indicator in result["indicators"]:
            technical_lines.append(
                f"{indicator['type']}: {indicator['value']}"
            )

        if not result["indicators"]:
            technical_lines.append("No indicators extracted.")

        ctk.CTkLabel(
            technical_content,
            text="\n".join(technical_lines),
            font=("Consolas", 11),
            text_color="#26352B",
            justify="left",
            wraplength=750
        ).pack(anchor="w", padx=15, pady=10)

        technical_content.pack_forget()
        technical._technical_content = technical_content
        technical._technical_button = technical_button

        ctk.CTkLabel(
            self.results_frame,
            text="Analysis performed locally. No links were opened.",
            font=("Arial", 11),
            text_color="#59675C"
        ).pack(pady=(5, 20))

    def toggle_technical(self, frame):
        content = frame._technical_content

        if content.winfo_manager():
            content.pack_forget()
            frame._technical_button.configure(
                text="SHOW TECHNICAL DETAILS"
            )
        else:
            content.pack(fill="x", padx=10, pady=(0, 10))
            frame._technical_button.configure(
                text="HIDE TECHNICAL DETAILS"
            )

    def build_footer(self):
        ctk.CTkLabel(
            self,
            text="GOLDEN AGE DIGITAL SECURITY",
            text_color="#D6B66B",
            font=("Arial", 11, "bold")
        ).grid(row=3, column=0, pady=(5, 15))


def start_private_session():
    global _session_lock_handle

    from database.init_db import set_database_path

    session_root = Path(tempfile.gettempdir()) / "WhiskeySessions"
    session_root.mkdir(parents=True, exist_ok=True)

    # Serialize recovery so two launches cannot interfere.
    recovery_lock_path = session_root / "recovery.lock"
    with open(recovery_lock_path, "a+b") as recovery_lock:
        if recovery_lock.seek(0, 2) == 0:
            recovery_lock.write(b"0")
            recovery_lock.flush()

        recovery_lock.seek(0)
        msvcrt.locking(recovery_lock.fileno(), msvcrt.LK_LOCK, 1)

        try:
            # Remove abandoned session directories.
            for old_session in session_root.iterdir():
                if not old_session.is_dir():
                    continue

                old_lock_path = old_session / "session.lock"

                try:
                    with open(old_lock_path, "r+b") as old_lock:
                        old_lock.seek(0)
                        msvcrt.locking(
                            old_lock.fileno(),
                            msvcrt.LK_NBLCK,
                            1
                        )
                        msvcrt.locking(
                            old_lock.fileno(),
                            msvcrt.LK_UNLCK,
                            1
                        )

                    shutil.rmtree(old_session)

                except (OSError, PermissionError):
                    # An active session holds its lock.
                    continue

            # Create this application's session.
            session_directory = Path(
                tempfile.mkdtemp(prefix="session_", dir=session_root)
            )

            lock_path = session_directory / "session.lock"
            _session_lock_handle = open(lock_path, "w+b")
            _session_lock_handle.write(b"0")
            _session_lock_handle.flush()
            _session_lock_handle.seek(0)

            msvcrt.locking(
                _session_lock_handle.fileno(),
                msvcrt.LK_NBLCK,
                1
            )

        finally:
            recovery_lock.seek(0)
            msvcrt.locking(
                recovery_lock.fileno(),
                msvcrt.LK_UNLCK,
                1
            )

    session_database = session_directory / "whiskey.db"
    set_database_path(session_database)
    initialize_database()

    def cleanup_session():
        global _session_lock_handle

        if _session_lock_handle is not None:
            try:
                _session_lock_handle.seek(0)
                msvcrt.locking(
                    _session_lock_handle.fileno(),
                    msvcrt.LK_UNLCK,
                    1
                )
            finally:
                _session_lock_handle.close()
                _session_lock_handle = None

        try:
            shutil.rmtree(session_directory)
        except FileNotFoundError:
            pass
        except OSError as error:
            raise RuntimeError(
                f"Whiskey could not remove temporary session data: {session_directory}"
            ) from error

        if session_directory.exists():
            raise RuntimeError(
                f"Temporary session data still exists: {session_directory}"
            )

    atexit.register(cleanup_session)
    return cleanup_session


_session_lock_handle = None

if __name__ == "__main__":
    cleanup_session = start_private_session()
    app = WhiskeyApp()

    try:
        app.mainloop()
    finally:
        cleanup_session()













