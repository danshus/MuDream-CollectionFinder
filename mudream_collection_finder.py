import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading
import os
import webbrowser

class MuDreamCollectionFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("MuDream Collection Finder")
        self.root.geometry("1150x880")
        self.root.configure(bg="#0f172a")
        
        # Modern font configuration
        self.title_font = ("Segoe UI", 22, "bold")
        self.heading_font = ("Segoe UI", 14, "bold")
        self.body_font = ("Segoe UI", 10)
        self.button_font = ("Segoe UI", 10, "bold")
        self.small_font = ("Segoe UI", 9)
        
        # Configuration
        self.config_file = "collection_config.json"
        self.api_url = "https://mudream.online/api/graphql"
        self.bearer_token = tk.StringVar()
        
        # Armor sets
        self.armor_sets = [
            "Leather", "Pad", "Vine", "Bronze", "Silk", "Bone", "Scale", "Wind",
            "Violent Wind", "Sphinx", "Brass", "Spirit", "Plate", "Legendary",
            "Red Winged", "Guardian", "Dragon", "Light Plate", "Sacred Fire",
            "Ancient", "Adamantine", "Storm Crow", "Storm Zahard", "Black Dragon",
            "Demonic", "Grand Soul", "Holy Spirit", "Dark Steel", "Dark Phoenix",
            "Thunder Hawk", "Great Dragon", "Dark Soul", "Hurricane", "Red Spirit",
            "Dark Master", "Storm Blitz", "Piercing Grove", "Dragon Knight",
            "Vengeance", "Sylphid Ray", "Volcano", "Sunlight", "Succubus", "Phoenix Soul"
        ]
        
        # Excellent options
        self.excellent_options = {
            'iml': 'MH (Increase maximum life)',
            'imsd': 'SD (Increase maximum SD)',
            'dd': 'DD (Damage decrease)',
            'rd': 'REF (Reflect Damage)',
            'dsr': 'DSR (Defense success rate)',
            'izdr': 'ZEN (Increase Zen drop rate)'
        }
        
        # Sets with missing pieces
        self.sets_missing_gloves = ['Sacred Fire', 'Storm Zahard', 'Piercing Grove', 'Phoenix Soul']
        self.sets_missing_helm = ['Volcano', 'Hurricane', 'Thunder Hawk', 'Storm Crow']
        
        # Currency options
        self.currencies = {
            'Bless': tk.StringVar(value=""),
            'Soul': tk.StringVar(value=""),
            'Life': tk.StringVar(value=""),
            'Chaos': tk.StringVar(value=""),
            'Creation': tk.StringVar(value=""),
            'Zen': tk.StringVar(value=""),
            'DC': tk.StringVar(value="")
        }
        
        self.piece_types = ['helm', 'armor', 'pants', 'gloves', 'boots']
        self.checkboxes = {}
        self.piece_frames = {}  # Store references to piece frames
        self.config = {'sets': {}}
        self.search_set_selection = tk.StringVar(value="All Sets")
        self.search_set_dropdown = None
        
        # Load existing config
        self.load_config()
        self.create_widgets()
    
    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    if 'sets' in loaded:
                        self.config = loaded
                    else:
                        if 'armor_set' in loaded and 'requirements' in loaded:
                            self.config = {
                                'sets': {
                                    loaded['armor_set']: loaded['requirements']
                                }
                            }
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")
                return False
        return False
    
    def save_current_set(self):
        """Save or update current set configuration"""
        set_name = self.selected_set.get()
        
        if not set_name:
            messagebox.showerror("Error", "Please select an armor set!")
            return False
        
        requirements = {}
        has_requirements = False
        
        for piece in self.piece_types:
            # Skip pieces that don't exist for this set
            if piece == 'gloves' and set_name in self.sets_missing_gloves:
                continue
            if piece == 'helm' and set_name in self.sets_missing_helm:
                continue
            
            selected = []
            for opt_code, var in self.checkboxes[piece].items():
                if var.get():
                    selected.append(opt_code)
                    has_requirements = True
            if selected:
                requirements[piece] = selected
        
        if not has_requirements:
            messagebox.showerror("Error", "Please select at least one excellent option!")
            return False
        
        action = "updated" if set_name in self.config['sets'] else "added"
        self.config['sets'][set_name] = requirements
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.update_configured_sets_display()
            
            # Count configured pieces
            configured_pieces = len([p for p, opts in requirements.items() if opts])
            total_pieces = 5
            if set_name in self.sets_missing_gloves:
                total_pieces -= 1
            if set_name in self.sets_missing_helm:
                total_pieces -= 1
            
            messagebox.showinfo("Success", f"{set_name} set {action} successfully!\n{configured_pieces}/{total_pieces} pieces configured\nTotal sets: {len(self.config['sets'])}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
            return False
    
    def delete_set(self, set_name):
        """Delete a configured set"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {set_name} set?"):
            if set_name in self.config['sets']:
                del self.config['sets'][set_name]
                try:
                    with open(self.config_file, 'w') as f:
                        json.dump(self.config, f, indent=2)
                    self.update_configured_sets_display()
                    messagebox.showinfo("Success", f"{set_name} set deleted!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def load_set_to_form(self, set_name):
        """Load a configured set into the form for editing"""
        self.selected_set.set(set_name)
        self.on_set_selection_changed()
    
    def on_set_selection_changed(self, *args):
        """Clear all checkboxes and load set config if it exists"""
        set_name = self.selected_set.get()
        
        # Clear all checkboxes first
        for piece in self.piece_types:
            for opt_code, var in self.checkboxes[piece].items():
                var.set(False)
        
        # Enable/disable piece frames based on set
        for piece in self.piece_types:
            if hasattr(self, 'piece_frames') and piece in self.piece_frames:
                piece_frame = self.piece_frames[piece]
                
                # Check if this piece should be disabled for this set
                should_disable = False
                if piece == 'gloves' and set_name in self.sets_missing_gloves:
                    should_disable = True
                elif piece == 'helm' and set_name in self.sets_missing_helm:
                    should_disable = True
                
                # Update frame and checkbox states
                if should_disable:
                    piece_frame.config(bg="#0f172a")  # Darker background
                    is_first_label = True
                    for widget in piece_frame.winfo_children():
                        if isinstance(widget, tk.Label):
                            # Add "N/A" indicator to the header (first label)
                            if is_first_label:
                                current_text = widget.cget('text')
                                if '(N/A)' not in current_text:
                                    widget.config(text=f"{current_text} (N/A)", fg="#475569")
                                else:
                                    widget.config(fg="#475569")
                                is_first_label = False
                        elif isinstance(widget, tk.Frame):
                            for cb in widget.winfo_children():
                                if isinstance(cb, tk.Checkbutton):
                                    cb.config(state='disabled', fg="#475569")
                else:
                    piece_frame.config(bg="#1e293b")  # Normal background
                    is_first_label = True
                    for widget in piece_frame.winfo_children():
                        if isinstance(widget, tk.Label):
                            if is_first_label:
                                # Remove "N/A" indicator from the header
                                current_text = widget.cget('text')
                                if ' (N/A)' in current_text:
                                    widget.config(text=current_text.replace(' (N/A)', ''), fg="#fbbf24")
                                else:
                                    widget.config(fg="#fbbf24")
                                is_first_label = False
                        elif isinstance(widget, tk.Frame):
                            for cb in widget.winfo_children():
                                if isinstance(cb, tk.Checkbutton):
                                    cb.config(state='normal', fg="#e2e8f0")
        
        # If this set is already configured, load its requirements
        if set_name and set_name in self.config['sets']:
            requirements = self.config['sets'][set_name]
            for piece, options in requirements.items():
                if piece in self.checkboxes:
                    for opt_code in options:
                        if opt_code in self.checkboxes[piece]:
                            self.checkboxes[piece][opt_code].set(True)
    
    def update_configured_sets_display(self):
        """Update the display of configured sets"""
        # Update count label
        if hasattr(self, 'sets_count_label'):
            self.sets_count_label.config(text=f"📚 Configured Sets ({len(self.config['sets'])} total)")
        
        for widget in self.configured_sets_frame.winfo_children():
            widget.destroy()
        
        if not self.config['sets']:
            empty_frame = tk.Frame(self.configured_sets_frame, bg="#0f172a")
            empty_frame.pack(pady=20)
            tk.Label(
                empty_frame,
                text="No sets configured yet",
                font=self.body_font,
                bg="#0f172a",
                fg="#64748b"
            ).pack()
            tk.Label(
                empty_frame,
                text="Select a set below and configure its requirements to get started",
                font=self.small_font,
                bg="#0f172a",
                fg="#475569"
            ).pack()
        else:
            for set_name, requirements in self.config['sets'].items():
                set_card = tk.Frame(self.configured_sets_frame, bg="#1e293b", padx=12, pady=8)
                set_card.pack(fill="x", pady=4, padx=5)
                
                pieces_with_req = [p for p, opts in requirements.items() if opts]
                
                # Calculate total pieces for this set
                total_pieces = 5
                if set_name in self.sets_missing_gloves:
                    total_pieces -= 1
                if set_name in self.sets_missing_helm:
                    total_pieces -= 1
                
                info_text = f"✓ {set_name}"
                detail_text = f"{len(pieces_with_req)}/{total_pieces} pieces configured"
                
                left_frame = tk.Frame(set_card, bg="#1e293b")
                left_frame.pack(side="left", fill="x", expand=True)
                
                tk.Label(
                    left_frame,
                    text=info_text,
                    font=("Segoe UI", 11, "bold"),
                    bg="#1e293b",
                    fg="#10b981",
                    anchor="w"
                ).pack(anchor="w")
                
                tk.Label(
                    left_frame,
                    text=detail_text,
                    font=self.small_font,
                    bg="#1e293b",
                    fg="#64748b",
                    anchor="w"
                ).pack(anchor="w")
                
                btn_frame = tk.Frame(set_card, bg="#1e293b")
                btn_frame.pack(side="right")
                
                edit_btn = self.create_modern_button(
                    btn_frame,
                    "✏️ Edit",
                    lambda s=set_name: self.load_set_to_form(s),
                    "#8b5cf6",
                    width=8
                )
                edit_btn.pack(side="left", padx=3)
                
                del_btn = self.create_modern_button(
                    btn_frame,
                    "🗑️",
                    lambda s=set_name: self.delete_set(s),
                    "#ef4444",
                    width=3
                )
                del_btn.pack(side="left", padx=3)
        
        self.update_search_dropdown()
    
    def create_modern_button(self, parent, text, command, bg_color, fg_color="white", width=None):
        """Create a modern styled button with hover effects"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 9, "bold"),
            bg=bg_color,
            fg=fg_color,
            activebackground=self.darken_color(bg_color),
            activeforeground=fg_color,
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=6,
            borderwidth=0
        )
        
        if width:
            btn.config(width=width)
        
        # Hover effects
        def on_enter(e):
            btn.config(bg=self.lighten_color(bg_color))
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def lighten_color(self, hex_color):
        """Lighten a hex color"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lighter = tuple(min(255, int(c * 1.15)) for c in rgb)
        return f"#{lighter[0]:02x}{lighter[1]:02x}{lighter[2]:02x}"
    
    def darken_color(self, hex_color):
        """Darken a hex color"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(max(0, int(c * 0.85)) for c in rgb)
        return f"#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}"
    
    def update_search_dropdown(self):
        """Update the search set dropdown with current configured sets"""
        if self.search_set_dropdown is not None and self.config['sets']:
            set_options = ["All Sets"] + list(self.config['sets'].keys())
            self.search_set_dropdown['values'] = set_options
            if self.search_set_selection.get() not in set_options:
                self.search_set_selection.set("All Sets")
    
    def create_widgets(self):
        # Style configuration for ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#0f172a', borderwidth=0)
        style.configure('TNotebook.Tab', background='#1e293b', foreground='#94a3b8', 
                       padding=[20, 10], font=self.heading_font)
        style.map('TNotebook.Tab', background=[('selected', '#8b5cf6')], 
                 foreground=[('selected', '#ffffff')])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.setup_frame = tk.Frame(self.notebook, bg="#0f172a")
        self.notebook.add(self.setup_frame, text="⚙️  Setup Collections")
        
        self.search_frame = tk.Frame(self.notebook, bg="#0f172a")
        self.notebook.add(self.search_frame, text="🔍  Search Market")
        
        self.create_setup_tab()
        self.create_search_tab()
        
        if self.config['sets']:
            self.notebook.select(1)
    
    def create_setup_tab(self):
        """Create the setup/configuration tab"""
        title = tk.Label(
            self.setup_frame,
            text="⚙️ Collections Setup",
            font=("Arial", 18, "bold"),
            bg="#1e293b",
            fg="#a78bfa"
        )
        title.pack(pady=10)
        
        subtitle = tk.Label(
            self.setup_frame,
            text="Configure all your collection sets (one-time setup, can be edited later)",
            font=("Arial", 9),
            bg="#1e293b",
            fg="#94a3b8"
        )
        subtitle.pack()
        
        configured_frame = tk.Frame(self.setup_frame, bg="#334155", padx=10, pady=10)
        configured_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            configured_frame,
            text=f"Configured Sets ({len(self.config['sets'])} total):",
            font=("Arial", 10, "bold"),
            bg="#334155",
            fg="#c4b5fd"
        ).pack(anchor="w")
        
        # Create scrollable frame for configured sets
        sets_container = tk.Frame(configured_frame, bg="#1e293b", height=150)
        sets_container.pack(fill="x", pady=5)
        sets_container.pack_propagate(False)  # Maintain fixed height
        
        sets_canvas = tk.Canvas(sets_container, bg="#1e293b", highlightthickness=0, height=150)
        sets_scrollbar = ttk.Scrollbar(sets_container, orient="vertical", command=sets_canvas.yview)
        self.configured_sets_frame = tk.Frame(sets_canvas, bg="#1e293b")
        
        self.configured_sets_frame.bind(
            "<Configure>",
            lambda e: sets_canvas.configure(scrollregion=sets_canvas.bbox("all"))
        )
        
        sets_canvas.create_window((0, 0), window=self.configured_sets_frame, anchor="nw")
        sets_canvas.configure(yscrollcommand=sets_scrollbar.set)
        
        sets_canvas.pack(side="left", fill="both", expand=True)
        sets_scrollbar.pack(side="right", fill="y")
        
        self.update_configured_sets_display()
        
        ttk.Separator(self.setup_frame, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        set_frame = tk.Frame(self.setup_frame, bg="#334155", padx=10, pady=10)
        set_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(
            set_frame,
            text="Add/Edit Armor Set:",
            font=("Arial", 10, "bold"),
            bg="#334155",
            fg="#c4b5fd"
        ).pack(anchor="w")
        
        self.selected_set = tk.StringVar()
        self.selected_set.trace('w', self.on_set_selection_changed)
        
        set_dropdown = ttk.Combobox(
            set_frame,
            textvariable=self.selected_set,
            values=self.armor_sets,
            state="readonly",
            font=("Arial", 10),
            width=30
        )
        set_dropdown.pack(anchor="w", pady=5)
        
        options_container = tk.Frame(self.setup_frame, bg="#1e293b")
        options_container.pack(fill="both", expand=True, padx=20, pady=5)
        
        canvas = tk.Canvas(options_container, bg="#334155", highlightthickness=0)
        scrollbar = ttk.Scrollbar(options_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#334155")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        tk.Label(
            scrollable_frame,
            text="Select Required Excellent Options for Each Piece:",
            font=("Arial", 10, "bold"),
            bg="#334155",
            fg="#c4b5fd"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        pieces_grid = tk.Frame(scrollable_frame, bg="#334155")
        pieces_grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        for idx, piece in enumerate(self.piece_types):
            piece_frame = tk.LabelFrame(
                pieces_grid,
                text=piece.upper(),
                font=("Arial", 9, "bold"),
                bg="#1e293b",
                fg="#fbbf24",
                padx=10,
                pady=10
            )
            piece_frame.grid(row=0, column=idx, padx=5, pady=5, sticky="n")
            
            self.checkboxes[piece] = {}
            for opt_code, opt_label in self.excellent_options.items():
                var = tk.BooleanVar()
                
                cb = tk.Checkbutton(
                    piece_frame,
                    text=opt_label.split('(')[0].strip(),
                    variable=var,
                    font=("Arial", 8),
                    bg="#1e293b",
                    fg="#cbd5e1",
                    selectcolor="#1e293b",
                    activebackground="#1e293b",
                    activeforeground="#ffffff"
                )
                cb.pack(anchor="w")
                self.checkboxes[piece][opt_code] = var
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        save_btn = tk.Button(
            self.setup_frame,
            text="💾 Save/Update This Set",
            command=self.save_current_set,
            font=("Arial", 12, "bold"),
            bg="#22c55e",
            fg="white",
            activebackground="#16a34a",
            activeforeground="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        save_btn.pack(pady=10)
    
    def create_search_tab(self):
        """Create the search tab with price filters"""
        # Title
        title_frame = tk.Frame(self.search_frame, bg="#0f172a")
        title_frame.pack(pady=15)
        
        title = tk.Label(
            title_frame,
            text="🔍 Search Market",
            font=self.title_font,
            bg="#0f172a",
            fg="#a78bfa"
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Find the best deals for your collection items",
            font=self.small_font,
            bg="#0f172a",
            fg="#94a3b8"
        )
        subtitle.pack()
        
        # Bearer Token card
        token_frame = tk.Frame(self.search_frame, bg="#1e293b", padx=12, pady=12)
        token_frame.pack(fill="x", padx=25, pady=5)
        
        tk.Label(
            token_frame,
            text="🔑 Authentication",
            font=self.heading_font,
            bg="#1e293b",
            fg="#a78bfa"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            token_frame,
            text="Paste your Bearer token from mudream.online (F12 > Network > 'graphql' > authorization header)",
            font=self.small_font,
            bg="#1e293b",
            fg="#64748b",
            wraplength=900,
            justify="left"
        ).pack(anchor="w", pady=(0, 8))
        
        token_entry = tk.Entry(
            token_frame,
            textvariable=self.bearer_token,
            font=self.body_font,
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="white",
            relief=tk.FLAT,
            borderwidth=2
        )
        token_entry.pack(fill="x", ipady=8)
        
        if self.config['sets']:
            # Set selection card
            set_frame = tk.Frame(self.search_frame, bg="#1e293b", padx=12, pady=12)
            set_frame.pack(fill="x", padx=25, pady=10)
            
            tk.Label(
                set_frame,
                text="📦 Choose What to Search",
                font=self.heading_font,
                bg="#1e293b",
                fg="#a78bfa"
            ).pack(anchor="w", pady=(0, 10))
            
            set_options = ["All Sets"] + list(self.config['sets'].keys())
            
            self.search_set_dropdown = ttk.Combobox(
                set_frame,
                textvariable=self.search_set_selection,
                values=set_options,
                state="readonly",
                font=self.body_font,
                width=45
            )
            self.search_set_dropdown.pack(anchor="w", pady=5)
            
            tk.Label(
                set_frame,
                text=f"💡 {len(self.config['sets'])} set(s) configured • Select 'All Sets' to search everything",
                font=self.small_font,
                bg="#1e293b",
                fg="#64748b"
            ).pack(anchor="w", pady=(5, 0))
        else:
            no_config = tk.Label(
                self.search_frame,
                text="⚠️ No collections configured • Go to Setup tab to configure your sets",
                font=self.heading_font,
                bg="#0f172a",
                fg="#fbbf24",
                pady=20
            )
            no_config.pack()
        
        # Price filters card
        price_frame = tk.Frame(self.search_frame, bg="#1e293b", padx=12, pady=12)
        price_frame.pack(fill="x", padx=25, pady=10)
        
        tk.Label(
            price_frame,
            text="💰 Price Filters (Optional)",
            font=self.heading_font,
            bg="#1e293b",
            fg="#a78bfa"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            price_frame,
            text="Set maximum prices • Leave empty for no limit",
            font=self.small_font,
            bg="#1e293b",
            fg="#64748b"
        ).pack(anchor="w", pady=(0, 12))
        
        currencies_grid = tk.Frame(price_frame, bg="#1e293b")
        currencies_grid.pack(fill="x")
        
        row = 0
        col = 0
        for currency_name, var in self.currencies.items():
            currency_frame = tk.Frame(currencies_grid, bg="#1e293b")
            currency_frame.grid(row=row, column=col, padx=10, pady=6, sticky="w")
            
            tk.Label(
                currency_frame,
                text=f"{currency_name}:",
                font=self.body_font,
                bg="#1e293b",
                fg="#cbd5e1",
                width=10,
                anchor="w"
            ).pack(side="left")
            
            entry = tk.Entry(
                currency_frame,
                textvariable=var,
                font=self.body_font,
                bg="#0f172a",
                fg="#e2e8f0",
                insertbackground="white",
                width=15,
                relief=tk.FLAT,
                borderwidth=1
            )
            entry.pack(side="left", ipady=5)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        if self.config['sets']:
            # Action buttons
            buttons_frame = tk.Frame(self.search_frame, bg="#0f172a")
            buttons_frame.pack(pady=15)
            
            search_btn = self.create_modern_button(
                buttons_frame,
                "🔍  Search Market",
                self.search_market,
                "#8b5cf6",
                width=18
            )
            search_btn.pack(side="left", padx=5)
            
            debug_btn = self.create_modern_button(
                buttons_frame,
                "🐛  Debug Mode",
                self.debug_search,
                "#64748b",
                width=15
            )
            debug_btn.pack(side="left", padx=5)
        
        # Results label
        results_label = tk.Label(
            self.search_frame,
            text="📊 Results",
            font=self.heading_font,
            bg="#0f172a",
            fg="#a78bfa"
        )
        results_label.pack(anchor="w", padx=25, pady=(10, 5))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            self.search_frame,
            font=("Consolas", 9),
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="white",
            height=15,
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.results_text.pack(fill="both", expand=True, padx=25, pady=(5, 20))
    
    def get_price_filters(self):
        """Get active price filters"""
        filters = {}
        for currency, var in self.currencies.items():
            value = var.get().strip()
            if value:
                try:
                    filters[currency] = float(value)
                except ValueError:
                    pass
        return filters
    
    def matches_price_filter(self, lot, price_filters):
        """Check if a lot matches the price filters"""
        if not price_filters:
            return True
        
        prices = lot.get('Prices', [])
        if not prices:
            return False
        
        currency_map = {
            'Bless': 'bless',
            'Soul': 'soul',
            'Life': 'life',
            'Chaos': 'chaos',
            'Creation': 'creat',
            'Zen': 'zen',
            'DC': 'dc'
        }
        
        api_filters = {}
        for user_name, limit in price_filters.items():
            api_code = currency_map.get(user_name)
            if api_code:
                api_filters[api_code] = limit
        
        jewel_codes = ['bless', 'soul', 'life', 'chaos', 'creat']
        jewel_filters = {k: v for k, v in api_filters.items() if k in jewel_codes}
        zen_filter = api_filters.get('zen')
        dc_filter = api_filters.get('dc')
        
        lot_prices = {}
        for price in prices:
            currency_code = price['Currency']['code'].lower()
            lot_prices[currency_code] = price['value']
        
        has_jewels = any(jewel in lot_prices for jewel in jewel_codes)
        has_zen = 'zen' in lot_prices
        has_dc = 'dc' in lot_prices
        
        if has_jewels and jewel_filters:
            for jewel in jewel_codes:
                if jewel in lot_prices:
                    if jewel not in jewel_filters:
                        return False
                    if lot_prices[jewel] > jewel_filters[jewel]:
                        return False
            return True
        
        if has_zen and zen_filter is not None:
            return lot_prices['zen'] <= zen_filter
        
        if has_dc and dc_filter is not None:
            return lot_prices['dc'] <= dc_filter
        
        return False
    
    def build_query(self, set_name, piece, options):
        """Build GraphQL query"""
        return {
            "operationName": "GET_ALL_LOTS",
            "query": """query GET_ALL_LOTS($offset: NonNegativeInt, $limit: NonNegativeInt, $sort: LotsSortInput, $filter: LotsFilterInput) {
                lots(limit: $limit, offset: $offset, sort: $sort, filter: $filter) {
                    Lots {
                        id
                        source
                        isMine
                        type
                        gearScore
                        hasPendingCounterOffer
                        Prices {
                            value
                            Currency {
                                id
                                code
                                type
                                title
                                __typename
                            }
                            __typename
                        }
                        Currencies {
                            id
                            code
                            type
                            title
                            isAvailableForLots
                            __typename
                        }
                        __typename
                    }
                    Pagination {
                        total
                        currentPage
                        nextPageExists
                        __typename
                    }
                    __typename
                }
            }""",
            "variables": {
                "filter": {
                    "name": set_name,
                    "type": [piece],
                    **options
                },
                "limit": 50,
                "offset": 0,
                "sort": {
                    "field": "LOT_FIELD_UPDATED_AT",
                    "type": "SORT_TYPE_DESC"
                }
            }
        }
    
    def calculate_normalized_price(self, lot):
        """Calculate normalized price based on jewel values"""
        prices = lot.get('Prices', [])
        if not prices:
            return float('inf')  # Items without price go to the end
        
        # Valuation: Life/Chaos = 1.0, Creation = 0.5, Bless/Soul = 0.25, DC = 0.125 (1/8)
        price_weights = {
            'life': 1.0,
            'chaos': 1.0,
            'creat': 0.5,
            'bless': 0.25,
            'soul': 0.25,
            'dc': 0.125,
            'zen': 0.0  # Zen not valued in comparison
        }
        
        total_value = 0.0
        for price in prices:
            currency_code = price['Currency']['code'].lower()
            value = price['value']
            weight = price_weights.get(currency_code, 0.0)
            total_value += value * weight
        
        return total_value
    
    def format_price(self, prices):
        """Format price display"""
        if not prices:
            return "No price listed"
        return " or ".join([f"{p['value']:,} {p['Currency']['code']}" for p in prices])
    
    def search_piece(self, set_name, piece, requirements, bearer_token, price_filters):
        """Search for a single piece"""
        # Skip pieces that don't exist for this set
        if piece == 'gloves' and set_name in self.sets_missing_gloves:
            return {
                'piece': piece,
                'set': set_name,
                'skipped': True,
                'message': 'This set has no gloves'
            }
        
        if piece == 'helm' and set_name in self.sets_missing_helm:
            return {
                'piece': piece,
                'set': set_name,
                'skipped': True,
                'message': 'This set has no helmet'
            }
        
        if not requirements or piece not in requirements:
            return {
                'piece': piece,
                'set': set_name,
                'skipped': True,
                'message': 'No requirements configured'
            }
        
        required_options = requirements[piece]
        if not required_options:
            return {
                'piece': piece,
                'set': set_name,
                'skipped': True,
                'message': 'No excellent options required'
            }
        
        options = {opt: [0, 1, 2, 3, 4] for opt in required_options}
        query = self.build_query(set_name, piece, options)
        
        try:
            token = bearer_token.replace('Bearer ', '').strip()
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
                'Accept': 'application/graphql-response+json, application/json'
            }
            
            response = requests.post(
                self.api_url,
                json=query,
                headers=headers,
                timeout=10
            )
            
            data = response.json()
            
            if 'data' in data and 'lots' in data['data']:
                all_lots = data['data']['lots']['Lots']
                filtered_lots = [lot for lot in all_lots if self.matches_price_filter(lot, price_filters)]
                
                # Sort by normalized price (cheapest first)
                filtered_lots.sort(key=self.calculate_normalized_price)
                
                return {
                    'piece': piece,
                    'set': set_name,
                    'total': len(all_lots),
                    'filtered_total': len(filtered_lots),
                    'lots': filtered_lots
                }
            else:
                return {
                    'piece': piece,
                    'set': set_name,
                    'error': True,
                    'message': 'Failed to fetch data or no data returned'
                }
        except Exception as e:
            return {
                'piece': piece,
                'set': set_name,
                'error': True,
                'message': str(e)
            }
    
    def display_results(self, all_results, price_filters):
        """Display results in text widget"""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        
        self.results_text.insert(tk.END, f"{'='*80}\n", "header")
        self.results_text.insert(tk.END, f"Search Results for All Configured Collections\n", "header")
        
        if price_filters:
            filter_text = ", ".join([f"{k} ≤ {v:,.0f}" for k, v in price_filters.items()])
            self.results_text.insert(tk.END, f"Price Filters: {filter_text}\n", "header")
        
        self.results_text.insert(tk.END, f"Sorted by price (cheapest first)\n", "header")
        self.results_text.insert(tk.END, f"Value calc: Life/Chaos=1.0, Creation=0.5, Bless/Soul=0.25, DC=0.125\n", "header")
        self.results_text.insert(tk.END, f"{'='*80}\n\n", "header")
        
        for set_name, results in all_results.items():
            self.results_text.insert(tk.END, f"\n{'█'*80}\n", "set_header")
            self.results_text.insert(tk.END, f"  {set_name} SET\n", "set_header")
            self.results_text.insert(tk.END, f"{'█'*80}\n\n", "set_header")
            
            for result in results:
                piece_name = result['piece'].upper()
                piece_type = result['piece']
                
                self.results_text.insert(tk.END, f"[{piece_name}]\n", "piece_header")
                self.results_text.insert(tk.END, "-" * 80 + "\n")
                
                if result.get('skipped'):
                    self.results_text.insert(tk.END, f"⊘ {result['message']}\n\n", "skipped")
                elif result.get('error'):
                    self.results_text.insert(tk.END, f"✗ ERROR: {result['message']}\n\n", "error")
                else:
                    total = result['total']
                    filtered = result['filtered_total']
                    
                    if price_filters:
                        self.results_text.insert(tk.END, f"Found {total} total, {filtered} match price filters\n\n", "info")
                    else:
                        self.results_text.insert(tk.END, f"Found {total} listing(s)\n\n", "info")
                    
                    # Get the required excellent options for this piece
                    required_opts = []
                    if set_name in self.config['sets'] and piece_type in self.config['sets'][set_name]:
                        opt_codes = self.config['sets'][set_name][piece_type]
                        opt_labels = {
                            'iml': 'MH', 'imsd': 'SD', 'dd': 'DD',
                            'rd': 'REF', 'dsr': 'DSR', 'izdr': 'ZEN'
                        }
                        required_opts = [opt_labels.get(code, code) for code in opt_codes]
                    
                    # Show search criteria
                    if required_opts and filtered > 0:
                        search_criteria = f"Set: {set_name} | Type: {piece_type} | Options: {'+'.join(required_opts)}"
                        self.results_text.insert(tk.END, f"🔍 To find in market: ", "search_label")
                        
                        # Make criteria copyable
                        criteria_tag = f"criteria_{set_name}_{piece_type}"
                        self.results_text.insert(tk.END, search_criteria, (criteria_tag, "criteria"))
                        
                        def make_copy_criteria_handler(criteria_text):
                            def handler(event):
                                self.root.clipboard_clear()
                                self.root.clipboard_append(criteria_text)
                                self.root.update()
                                messagebox.showinfo("Copied!", f"Search criteria copied!\n\n{criteria_text}", parent=self.root)
                            return handler
                        
                        self.results_text.tag_bind(criteria_tag, "<Button-1>", make_copy_criteria_handler(search_criteria))
                        self.results_text.tag_bind(criteria_tag, "<Enter>",
                            lambda e: self.results_text.config(cursor="hand2"))
                        self.results_text.tag_bind(criteria_tag, "<Leave>",
                            lambda e: self.results_text.config(cursor=""))
                        
                        # Add open market button
                        self.results_text.insert(tk.END, " ", "detail")
                        market_tag = f"market_{set_name}_{piece_type}"
                        self.results_text.insert(tk.END, "[Open Market]", (market_tag, "market_link"))
                        
                        def make_market_handler():
                            def handler(event):
                                webbrowser.open("https://mudream.online/market")
                            return handler
                        
                        self.results_text.tag_bind(market_tag, "<Button-1>", make_market_handler())
                        self.results_text.tag_bind(market_tag, "<Enter>",
                            lambda e: self.results_text.config(cursor="hand2"))
                        self.results_text.tag_bind(market_tag, "<Leave>",
                            lambda e: self.results_text.config(cursor=""))
                        
                        self.results_text.insert(tk.END, "\n", "detail")
                        self.results_text.insert(tk.END, f"💡 Click criteria to copy, then apply filters manually in market\n\n", "hint")
                    
                    if result['lots']:
                        for idx, lot in enumerate(result['lots'], 1):
                            price = self.format_price(lot['Prices'])
                            gs = f" (GS: {lot['gearScore']})" if lot.get('gearScore') else ""
                            mine = " ⭐ YOUR ITEM" if lot.get('isMine') else ""
                            
                            # Calculate normalized price for display
                            norm_price = self.calculate_normalized_price(lot)
                            norm_display = f" [Value: {norm_price:.2f}]" if norm_price != float('inf') else ""
                            
                            friendly_name = f"{set_name} {piece_name.title()} #{idx}"
                            
                            self.results_text.insert(tk.END, f"  {idx}. {friendly_name}{gs}{mine}{norm_display}\n", "item_name")
                            self.results_text.insert(tk.END, f"     💰 {price}\n", "price")
                            self.results_text.insert(tk.END, f"     📦 {lot.get('source', 'Market')}\n\n", "detail")
                    else:
                        self.results_text.insert(tk.END, "  No items match your price filters\n\n", "no_results")
        
        self.results_text.tag_config("header", foreground="#a78bfa", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("set_header", foreground="#fbbf24", font=("Consolas", 11, "bold"))
        self.results_text.tag_config("piece_header", foreground="#c4b5fd", font=("Consolas", 9, "bold"))
        self.results_text.tag_config("info", foreground="#94a3b8")
        self.results_text.tag_config("search_label", foreground="#94a3b8", font=("Consolas", 9))
        self.results_text.tag_config("criteria", foreground="#fbbf24", font=("Consolas", 9, "bold", "underline"))
        self.results_text.tag_config("item_name", foreground="#e2e8f0", font=("Consolas", 9, "bold"))
        self.results_text.tag_config("market_link", foreground="#22c55e", font=("Consolas", 9, "bold", "underline"))
        self.results_text.tag_config("hint", foreground="#64748b", font=("Consolas", 8, "italic"))
        self.results_text.tag_config("price", foreground="#22c55e", font=("Consolas", 9, "bold"))
        self.results_text.tag_config("detail", foreground="#94a3b8", font=("Consolas", 8))
        self.results_text.tag_config("skipped", foreground="#94a3b8", font=("Consolas", 9, "italic"))
        self.results_text.tag_config("error", foreground="#ef4444")
        self.results_text.tag_config("no_results", foreground="#94a3b8", font=("Consolas", 9, "italic"))
    
    def search_thread(self):
        """Run search in separate thread"""
        if not self.config['sets']:
            messagebox.showerror("Error", "No collections configured! Go to Setup tab first.")
            return
        
        bearer_token = self.bearer_token.get().strip()
        
        if not bearer_token:
            messagebox.showerror("Error", "Please enter your Bearer token!")
            return
        
        selected_set = self.search_set_selection.get()
        
        if selected_set == "All Sets":
            sets_to_search = self.config['sets']
            search_count = len(sets_to_search)
        else:
            if selected_set not in self.config['sets']:
                messagebox.showerror("Error", f"Set '{selected_set}' not found in configuration!")
                return
            sets_to_search = {selected_set: self.config['sets'][selected_set]}
            search_count = 1
        
        price_filters = self.get_price_filters()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🔍 Searching {search_count} set(s)...\n\n")
        
        all_results = {}
        
        for set_name, requirements in sets_to_search.items():
            self.results_text.insert(tk.END, f"Searching {set_name}...\n")
            set_results = []
            
            for piece in self.piece_types:
                result = self.search_piece(set_name, piece, requirements, bearer_token, price_filters)
                set_results.append(result)
                self.results_text.insert(tk.END, f"  - {piece}...\n")
            
            all_results[set_name] = set_results
        
        self.display_results(all_results, price_filters)
    
    def search_market(self):
        """Start search in thread"""
        thread = threading.Thread(target=self.search_thread, daemon=True)
        thread.start()
    
    def debug_search_thread(self):
        """Debug search to see raw price data"""
        if not self.config['sets']:
            messagebox.showerror("Error", "No collections configured!")
            return
        
        bearer_token = self.bearer_token.get().strip()
        if not bearer_token:
            messagebox.showerror("Error", "Please enter your Bearer token!")
            return
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "🐛 DEBUG MODE - Showing first 5 items with raw price data\n")
        self.results_text.insert(tk.END, "="*80 + "\n\n")
        
        for set_name, requirements in self.config['sets'].items():
            for piece in self.piece_types:
                if piece not in requirements or not requirements[piece]:
                    continue
                
                options = {opt: [0, 1, 2, 3, 4] for opt in requirements[piece]}
                query = self.build_query(set_name, piece, options)
                
                try:
                    token = bearer_token.replace('Bearer ', '').strip()
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/graphql-response+json, application/json'
                    }
                    
                    response = requests.post(self.api_url, json=query, headers=headers, timeout=10)
                    data = response.json()
                    
                    if 'data' in data and 'lots' in data['data']:
                        lots = data['data']['lots']['Lots'][:5]
                        
                        self.results_text.insert(tk.END, f"Set: {set_name}, Piece: {piece}\n")
                        self.results_text.insert(tk.END, f"Found {len(lots)} items (showing first 5)\n\n")
                        
                        for idx, lot in enumerate(lots, 1):
                            self.results_text.insert(tk.END, f"--- Item {idx} (Lot #{lot['id']}) ---\n")
                            self.results_text.insert(tk.END, f"Prices array:\n")
                            
                            for price in lot.get('Prices', []):
                                currency = price['Currency']
                                self.results_text.insert(tk.END, f"  • Value: {price['value']}\n")
                                self.results_text.insert(tk.END, f"    Code: '{currency['code']}'\n")
                                self.results_text.insert(tk.END, f"    Title: '{currency.get('title', 'N/A')}'\n")
                                self.results_text.insert(tk.END, f"    Type: '{currency.get('type', 'N/A')}'\n\n")
                            
                            self.results_text.insert(tk.END, "\n")
                        
                        return
                        
                except Exception as e:
                    self.results_text.insert(tk.END, f"Error: {e}\n")
                    continue
    
    def debug_search(self):
        """Start debug search in thread"""
        thread = threading.Thread(target=self.debug_search_thread, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MuDreamCollectionFinder(root)
    root.mainloop()