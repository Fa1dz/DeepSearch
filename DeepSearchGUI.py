import customtkinter as ctk
from tkinter import scrolledtext, messagebox, filedialog
import json
import threading
import csv
from DeepSearch import deep_search

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DeepSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DeepSearch Advanced - AI-Powered Analysis")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 700)

        self.search_thread = None
        self.current_results = None
        self.is_searching = False

        self.create_ui()

    def create_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # ========== HEADER ==========
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            header,
            text="🔍 DeepSearch Advanced",
            font=("Helvetica", 32, "bold"),
            text_color="#00D9FF"
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            header,
            text="AI-Powered Web Search & Reasoning Engine",
            font=("Helvetica", 14),
            text_color="#888888"
        )
        subtitle.pack(side="left", padx=20)

        # ========== SEARCH INPUT ==========
        search_frame = ctk.CTkFrame(main_frame, fg_color="#1f1f1f", corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 15))

        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Query:",
            font=("Helvetica", 12, "bold")
        )
        search_label.pack(anchor="w", padx=15, pady=(10, 5))

        input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter your search query...",
            height=40,
            font=("Helvetica", 12)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.start_search())

        self.search_button = ctk.CTkButton(
            input_frame,
            text="🔎 Search",
            command=self.start_search,
            width=100,
            height=40,
            font=("Helvetica", 12, "bold")
        )
        self.search_button.pack(side="left", padx=(0, 5))

        self.stop_button = ctk.CTkButton(
            input_frame,
            text="⏹ Stop",
            command=self.stop_search,
            width=100,
            height=40,
            fg_color="#ff4444",
            hover_color="#cc0000",
            state="disabled"
        )
        self.stop_button.pack(side="left")

        # ========== OPTIONS ==========
        options_frame = ctk.CTkFrame(main_frame, fg_color="#1f1f1f", corner_radius=10)
        options_frame.pack(fill="x", pady=(0, 15))

        opts_label = ctk.CTkLabel(
            options_frame,
            text="Options:",
            font=("Helvetica", 11, "bold")
        )
        opts_label.pack(anchor="w", padx=15, pady=(10, 5))

        opts_inner = ctk.CTkFrame(options_frame, fg_color="transparent")
        opts_inner.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(opts_inner, text="Max Results:", font=("Helvetica", 10)).pack(side="left", padx=(0, 5))
        self.max_results = ctk.CTkComboBox(opts_inner, values=["5", "10", "15", "20", "30"], width=80)
        self.max_results.set("15")
        self.max_results.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(opts_inner, text="Max Fetch:", font=("Helvetica", 10)).pack(side="left", padx=(0, 5))
        self.max_fetch = ctk.CTkComboBox(opts_inner, values=["1", "3", "5", "10"], width=80)
        self.max_fetch.set("5")
        self.max_fetch.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(opts_inner, text="Delay (sec):", font=("Helvetica", 10)).pack(side="left", padx=(0, 5))
        self.delay = ctk.CTkComboBox(opts_inner, values=["0.5", "1.0", "2.0", "3.0"], width=80)
        self.delay.set("1.0")
        self.delay.pack(side="left", padx=(0, 20))

        save_btn = ctk.CTkButton(opts_inner, text="💾 Save JSON", command=self.save_results, width=120)
        save_btn.pack(side="right", padx=(0, 10))

        export_btn = ctk.CTkButton(opts_inner, text="📊 Export CSV", command=self.export_csv, width=120)
        export_btn.pack(side="right", padx=(0, 10))

        # ========== PROGRESS ==========
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(0, 15))

        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready to search", font=("Helvetica", 10), text_color="#888888")
        self.progress_label.pack(anchor="w")

        self.progress = ctk.CTkProgressBar(progress_frame, height=6)
        self.progress.pack(fill="x", pady=(5, 0))
        self.progress.set(0)

        # ========== INSIGHTS PANEL ==========
        insights_frame = ctk.CTkFrame(main_frame, fg_color="#1f1f1f", corner_radius=10)
        insights_frame.pack(fill="x", pady=(0, 15))

        insights_title = ctk.CTkLabel(insights_frame, text="💡 Insights & Analysis", font=("Helvetica", 12, "bold"))
        insights_title.pack(anchor="w", padx=15, pady=(10, 10))

        self.insights_text = scrolledtext.ScrolledText(
            insights_frame,
            wrap="word",
            font=("Courier", 9),
            bg="#2b2b2b",
            fg="#ffff00",
            height=4,
            insertbackground="#ffff00"
        )
        self.insights_text.pack(fill="x", padx=15, pady=(0, 15))

        # ========== MAIN RESULTS AREA ==========
        results_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        results_container.pack(fill="both", expand=True)

        # Left: Results
        left_frame = ctk.CTkFrame(results_container, fg_color="#1f1f1f", corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        left_title = ctk.CTkLabel(left_frame, text="📋 Search Results", font=("Helvetica", 12, "bold"))
        left_title.pack(anchor="w", padx=15, pady=(10, 10))

        self.results_text = scrolledtext.ScrolledText(
            left_frame, wrap="word", font=("Courier", 8), bg="#2b2b2b", fg="#00ff00", insertbackground="#00ff00"
        )
        self.results_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.results_text.tag_config("title", foreground="#00ff00", font=("Courier", 8, "bold"))
        self.results_text.tag_config("url", foreground="#ffaa00")
        self.results_text.tag_config("marker", foreground="#ff00ff")
        self.results_text.tag_config("info", foreground="#00ccff")
        self.results_text.tag_config("sentiment_pos", foreground="#00ff00")
        self.results_text.tag_config("sentiment_neg", foreground="#ff6666")
        self.results_text.bind("<Button-1>", self.on_result_click)

        # Right: Details
        right_frame = ctk.CTkFrame(results_container, fg_color="#1f1f1f", corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        right_title = ctk.CTkLabel(right_frame, text="🔎 Advanced Details", font=("Helvetica", 12, "bold"))
        right_title.pack(anchor="w", padx=15, pady=(10, 10))

        self.details_text = scrolledtext.ScrolledText(
            right_frame, wrap="word", font=("Courier", 8), bg="#2b2b2b", fg="#00ccff", insertbackground="#00ccff"
        )
        self.details_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def start_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Input", "Please enter a search query")
            return

        self.search_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.details_text.delete("1.0", "end")
        self.insights_text.delete("1.0", "end")
        self.progress.set(0)
        self.progress_label.configure(text="⏳ Searching...")
        self.is_searching = True

        max_res = int(self.max_results.get())
        max_f = int(self.max_fetch.get())
        del_sec = float(self.delay.get())

        self.search_thread = threading.Thread(
            target=self._search_worker,
            args=(query, max_res, max_f, del_sec),
            daemon=True
        )
        self.search_thread.start()

    def _search_worker(self, query, max_res, max_f, delay_sec):
        try:
            self.current_results = deep_search(query, max_results=max_res, max_fetch=max_f, delay=delay_sec)
            self.root.after(0, self._display_results)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.is_searching = False
            self.root.after(0, self._finish_search)

    def _display_results(self):
        if not self.current_results:
            return

        results = self.current_results.get("results", [])
        insights = self.current_results.get("insights", {})

        # Display insights
        self.insights_text.delete("1.0", "end")
        self.insights_text.insert("end", f"🎯 Overall Credibility: {insights.get('overall_credibility', 0)}\n", "info")
        self.insights_text.insert("end", f"📊 Key Topics: {', '.join(list(insights.get('key_topics', {}).keys())[:5])}\n", "info")
        self.insights_text.insert("end", f"🌐 Language Distribution: {insights.get('language_distribution', {})}\n", "info")

        # Display results
        self.results_text.delete("1.0", "end")
        self.results_text.insert("end", f"Query: {self.current_results['query']}\n", "title")
        self.results_text.insert("end", f"Results: {len(results)}\n", "info")
        self.results_text.insert("end", "─" * 80 + "\n\n")

        for i, r in enumerate(results, 1):
            title = r.get("title") or "(No title)"
            href = r.get("href") or ""
            fetched = "✓" if r.get("fetched") else "✗"

            self.results_text.insert("end", f"[{i}] {fetched} ", "marker")
            self.results_text.insert("end", f"{title}\n", "title")
            self.results_text.insert("end", f"    {href}\n", "url")

            if r.get("analysis"):
                a = r["analysis"]
                self.results_text.insert("end", f"    Credibility: {a.get('credibility_score', 0)} | Words: {a.get('word_count')}\n", "info")
                
                if a.get("sentiment"):
                    s = a["sentiment"]
                    tag = "sentiment_pos" if s["sentiment"] == "Positive" else "sentiment_neg" if s["sentiment"] == "Negative" else "info"
                    self.results_text.insert("end", f"    Sentiment: {s['sentiment']} ({s['polarity']})\n", tag)

            self.results_text.insert("end", "\n")

    def on_result_click(self, event):
        if not self.current_results:
            return
        
        line = self.results_text.index(f"@{event.x},{event.y}").split(".")[0]
        line_text = self.results_text.get(f"{line}.0", f"{line}.end")

        for i, r in enumerate(self.current_results.get("results", []), 1):
            if f"[{i}]" in line_text:
                self._show_result_details(r, i)
                break

    def _show_result_details(self, result, idx):
        self.details_text.delete("1.0", "end")

        title = result.get("title") or "(No title)"
        href = result.get("href") or ""
        snippet = result.get("snippet") or ""

        self.details_text.insert("end", f"Result #{idx}: {title}\n", "title")
        self.details_text.insert("end", "═" * 60 + "\n\n")

        self.details_text.insert("end", "URL:\n")
        self.details_text.insert("end", f"{href}\n\n", "url")

        if result.get("analysis"):
            a = result["analysis"]
            self.details_text.insert("end", "ANALYSIS:\n", "title")
            self.details_text.insert("end", f"  Credibility: {a.get('credibility_score')}\n")
            self.details_text.insert("end", f"  Words: {a.get('word_count')} | Avg Word Length: {a.get('avg_word_length')}\n")
            self.details_text.insert("end", f"  Readability: {a.get('readability_score')}\n")
            self.details_text.insert("end", f"  Language: {a.get('language')}\n\n")

            if a.get("sentiment"):
                s = a["sentiment"]
                self.details_text.insert("end", f"SENTIMENT:\n  {s['sentiment']} | Polarity: {s['polarity']} | Subjectivity: {s['subjectivity']}\n\n")

            if a.get("keyphrases"):
                self.details_text.insert("end", "KEY PHRASES:\n")
                for kp in a["keyphrases"][:10]:
                    self.details_text.insert("end", f"  • {kp['phrase']} (×{kp['count']})\n")
                self.details_text.insert("end", "\n")

            if a.get("named_entities"):
                self.details_text.insert("end", "ENTITIES:\n")
                for ent_type, ents in a["named_entities"].items():
                    self.details_text.insert("end", f"  {ent_type}: {', '.join(ents)}\n")

    def _finish_search(self):
        self.progress.set(1.0)
        self.progress_label.configure(text="✓ Search complete")
        self.search_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def stop_search(self):
        self.is_searching = False
        self.stop_button.configure(state="disabled")
        self.search_button.configure(state="normal")
        self.progress_label.configure(text="⏹ Search stopped")

    def save_results(self):
        if not self.current_results:
            messagebox.showinfo("No Data", "No results to save")
            return

        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.current_results, f, indent=2)
            messagebox.showinfo("Saved", f"Results saved to {path}")

    def export_csv(self):
        if not self.current_results:
            messagebox.showinfo("No Data", "No results to export")
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            results = self.current_results.get("results", [])
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Index", "Title", "URL", "Credibility", "Words", "Sentiment", "Language"])
                for i, r in enumerate(results, 1):
                    a = r.get("analysis", {})
                    sentiment = a.get("sentiment", {}).get("sentiment", "N/A") if a.get("sentiment") else "N/A"
                    writer.writerow([i, r.get("title", ""), r.get("href", ""), a.get("credibility_score", 0), a.get("word_count", 0), sentiment, a.get("language", "unknown")])
            messagebox.showinfo("Exported", f"Results exported to {path}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = DeepSearchGUI(root)
    root.mainloop()