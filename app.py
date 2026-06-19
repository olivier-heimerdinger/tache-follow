import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
from datetime import datetime
import os
import shutil

class UltimateFlexibleTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("950x680")
        
        # Textes par défaut de l'UI
        self.ui_texts = {
            "app_title": "Orchestrateur de Tâches - V5",
            "welcome_title": "🚀 Configuration de l'Orchestrateur",
            "yaml_section_title": "1. Sélection du fichier de configuration (YAML)",
            "dest_section_title": "2. Destination des rapports d'exécution",
            "btn_browse": "📁 Ouvrir un fichier...",
            "btn_change_dest": "✏️ Modifier le dossier...",
            "btn_launch": "▶️ Initialiser et Lancer l'Exécution",
            "timeline_title": "Timeline des Étapes",
            "action_title": "Action active",
            "btn_validate": "💾 Valider l'étape et Enregistrer",
            "end_success": "🎉 Fin du suivi. Toutes les tâches ont été traitées !",
            "end_blocked": "🛑 PROCESSUS INTERROMPU (Erreur Bloquante)",
            "btn_open_folder": "📂 Ouvrir le dossier du rapport",
            "btn_new_proc": "🔄 Nouvelle Procédure",
            "btn_quit": "❌ Quitter l'application"
        }
        self.load_ui_config()
        self.root.title(self.ui_texts["app_title"])
        
        self.reset_variables()
        self.setup_initial_ui()

    def load_ui_config(self):
        """Charge le fichier config_ui.yml s'il existe pour personnaliser les textes."""
        if os.path.exists("config_ui.yml"):
            try:
                with open("config_ui.yml", "r", encoding="utf-8") as f:
                    custom_ui = yaml.safe_load(f)
                    if custom_ui and isinstance(custom_ui, dict):
                        self.ui_texts.update(custom_ui)
            except Exception as e:
                print(f"Erreur lors de la lecture de config_ui.yml : {e}")

    def reset_variables(self):
        """Réinitialise les variables d'état pour une nouvelle procédure."""
        self.tasks = []
        self.current_index = 0
        self.yaml_file = None
        self.output_root_dir = None
        self.execution_dir = None
        self.main_log_file = None
        self.attached_image_path = None

    def clear_window(self):
        """Détruit tous les widgets de la fenêtre principale."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def reset_app(self):
        """Nettoie l'interface et relance l'écran d'accueil."""
        self.clear_window()
        self.reset_variables()
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.welcome_frame = ttk.Frame(self.root, padding=30)
        self.welcome_frame.pack(expand=True, fill=tk.BOTH)
        
        lbl_title = tk.Label(self.welcome_frame, text=self.ui_texts["welcome_title"], font=("Helvetica", 16, "bold"))
        lbl_title.pack(pady=(0, 20))
        
        yaml_frame = ttk.LabelFrame(self.welcome_frame, text=self.ui_texts["yaml_section_title"], padding=15)
        yaml_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_yaml_status = tk.Label(yaml_frame, text="En attente d'un fichier...", fg="orange", font=("Helvetica", 10, "italic"), anchor="w")
        self.lbl_yaml_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        btn_browse_yaml = ttk.Button(yaml_frame, text=self.ui_texts["btn_browse"], command=self.browse_yaml)
        btn_browse_yaml.pack(side=tk.RIGHT)

        self.dest_frame = ttk.LabelFrame(self.welcome_frame, text=self.ui_texts["dest_section_title"], padding=15)
        self.lbl_auto_dest = tk.Label(self.dest_frame, text="En attente...", fg="gray", justify="left", anchor="w")
        self.lbl_auto_dest.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.btn_change_dest = ttk.Button(self.dest_frame, text=self.ui_texts["btn_change_dest"], command=self.change_output_dir)
        self.btn_change_dest.pack(side=tk.RIGHT, padx=5)

        self.btn_launch = ttk.Button(self.welcome_frame, text=self.ui_texts["btn_launch"], state=tk.DISABLED, command=self.launch_orchestrator)
        self.btn_launch.pack(fill=tk.X, ipady=12, pady=(30, 10))

    def browse_yaml(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier YAML",
            filetypes=[("Fichiers YAML", "*.yml *.yaml"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self.yaml_file = filename
            self.lbl_yaml_status.config(text=f"Fichier chargé : {os.path.basename(filename)}", fg="green", font=("Helvetica", 10, "bold"))
            yaml_dir = os.path.dirname(self.yaml_file)
            self.output_root_dir = os.path.join(yaml_dir, "RAPPORT_TACHE")
            
            self.dest_frame.pack(fill=tk.X, pady=15)
            self.update_dest_label(is_custom=False)
            self.btn_launch.config(state=tk.NORMAL)

    def change_output_dir(self):
        initial_dir = os.path.dirname(self.yaml_file) if self.yaml_file else "/"
        directory = filedialog.askdirectory(title="Choisir le dossier racine", initialdir=initial_dir)
        if directory:
            self.output_root_dir = directory
            self.update_dest_label(is_custom=True)

    def update_dest_label(self, is_custom=False):
        prefix = "📂 Dossier personnalisé :" if is_custom else "📂 Dossier automatique :"
        color = "#2e7d32" if is_custom else "#0277bd"
        self.lbl_auto_dest.config(text=f"{prefix}\n👉 {self.output_root_dir}", fg=color, font=("Helvetica", 10, "bold"))

    def launch_orchestrator(self):
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.tasks = data.get('taches', [])
        except Exception as e:
            messagebox.showerror("Erreur", f"Lecture YAML impossible :\n{e}")
            return
            
        if not self.tasks:
            messagebox.showwarning("Attention", "Aucune tâche trouvée.")
            return

        iso_timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        self.execution_dir = os.path.join(self.output_root_dir, iso_timestamp)
        
        try:
            os.makedirs(self.execution_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Création du dossier impossible :\n{e}")
            return
            
        self.main_log_file = os.path.join(self.execution_dir, "rapport_general.md")
        self.init_main_log()

        self.clear_window()
        self.setup_main_ui()
        self.update_ui()

    def init_main_log(self):
        with open(self.main_log_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📋 Rapport Général d'Exécution\n\n")
            f.write(f"- **Fichier source :** `{os.path.basename(self.yaml_file)}`\n")
            f.write(f"- **Date :** {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
            f.write(f"- **Stockage :** `{self.execution_dir}`\n\n---\n\n")
            f.write("| ID | Nom de la Tâche | Statut | Criticité | Observations / Fichiers Attachés |\n")
            f.write("| :---: | :--- | :---: | :---: | :--- |\n")

    def setup_main_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        left_frame = ttk.LabelFrame(self.root, text=self.ui_texts["timeline_title"], padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        columns = ("id", "nom", "bloquante", "statut")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="none")
        self.tree.heading("id", text="#")
        self.tree.heading("nom", text="Tâche")
        self.tree.heading("bloquante", text="Bloq.")
        self.tree.heading("statut", text="Statut")
        
        self.tree.column("id", width=30, anchor="center")
        self.tree.column("nom", width=160)
        self.tree.column("bloquante", width=50, anchor="center")
        self.tree.column("statut", width=90, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        for task in self.tasks:
            is_blocking = "🔴 Oui" if task.get('bloquante', False) else "🟢 Non"
            self.tree.insert("", tk.END, iid=task['id'], values=(task['id'], task['nom'], is_blocking, "En attente"))

        self.right_frame = ttk.LabelFrame(self.root, text=self.ui_texts["action_title"], padding=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_task_name = tk.Label(self.right_frame, text="Tâche : -", font=("Helvetica", 12, "bold"), wraplength=480, justify="left")
        self.lbl_task_name.pack(anchor="w", pady=(0, 2))
        
        self.lbl_blocking_status = tk.Label(self.right_frame, text="", font=("Helvetica", 9, "italic"))
        self.lbl_blocking_status.pack(anchor="w", pady=(0, 10))

        # Conteneur des actions (Sera masqué à la fin)
        self.action_container = ttk.Frame(self.right_frame)
        self.action_container.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.action_container, text="✏️ Commentaire abrégé :").pack(anchor="w")
        self.text_short_comment = ttk.Entry(self.action_container, width=60)
        self.text_short_comment.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.action_container, text="📝 Détails / Logs :").pack(anchor="w")
        self.text_long_details = tk.Text(self.action_container, height=10, width=50, font=("Consolas", 10))
        self.text_long_details.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        img_frame = ttk.Frame(self.action_container)
        img_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(img_frame, text="🖼️ Capture :").pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_img_status = tk.Label(img_frame, text="Aucune image", fg="gray", font=("Helvetica", 9, "italic"))
        self.lbl_img_status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_attach_img = ttk.Button(img_frame, text="Parcourir...", command=self.attach_image)
        btn_attach_img.pack(side=tk.RIGHT)

        control_subframe = ttk.Frame(self.action_container)
        control_subframe.pack(fill=tk.X, pady=(0, 15))

        self.status_var = tk.StringVar(value="Succès")
        tk.Radiobutton(control_subframe, text="✅ Succès", variable=self.status_var, value="Succès", font=("Helvetica", 10, "bold"), command=self.toggle_error_menu).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(control_subframe, text="❌ Erreur", variable=self.status_var, value="Erreur", font=("Helvetica", 10, "bold"), command=self.toggle_error_menu).pack(side=tk.LEFT, padx=10)

        self.lbl_error_level = tk.Label(control_subframe, text="Criticité :")
        self.cb_error_level = ttk.Combobox(control_subframe, values=["Faible", "Moyen", "Critique"], state="disabled", width=20)
        self.cb_error_level.set("Moyen")
        self.lbl_error_level.pack(side=tk.LEFT, padx=(20, 5))
        self.cb_error_level.pack(side=tk.LEFT)

        self.btn_validate = ttk.Button(self.action_container, text=self.ui_texts["btn_validate"], command=self.validate_task)
        self.btn_validate.pack(fill=tk.X, ipady=8)

        # Conteneur de Fin (Masqué par défaut)
        self.end_container = ttk.Frame(self.right_frame)
        
        btn_open = ttk.Button(self.end_container, text=self.ui_texts["btn_open_folder"], command=self.open_report_folder)
        btn_open.pack(fill=tk.X, ipady=10, pady=10)
        
        btn_new = ttk.Button(self.end_container, text=self.ui_texts["btn_new_proc"], command=self.reset_app)
        btn_new.pack(fill=tk.X, ipady=10, pady=10)
        
        btn_quit = ttk.Button(self.end_container, text=self.ui_texts["btn_quit"], command=self.root.destroy)
        btn_quit.pack(fill=tk.X, ipady=10, pady=10)

    def attach_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.gif"), ("Tous", "*.*")])
        if filename:
            self.attached_image_path = filename
            self.lbl_img_status.config(text=os.path.basename(filename), fg="green")

    def toggle_error_menu(self):
        self.cb_error_level.config(state="readonly" if self.status_var.get() == "Erreur" else "disabled")

    def open_report_folder(self):
        """Ouvre l'explorateur Windows sur le dossier parent des rapports."""
        if self.output_root_dir and os.path.exists(self.output_root_dir):
            os.startfile(self.output_root_dir)

    def trigger_end_state(self, message, is_blocked=False):
        """Cache les contrôles d'action et affiche les boutons de fin."""
        self.lbl_task_name.config(text=message, fg="red" if is_blocked else "green")
        self.lbl_blocking_status.config(text="")
        
        # Cacher les actions, afficher les boutons de fin
        self.action_container.pack_forget()
        self.end_container.pack(fill=tk.BOTH, expand=True, pady=20)
        
        with open(self.main_log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n**Fin de session :** {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")

    def update_ui(self):
        self.attached_image_path = None
        self.lbl_img_status.config(text="Aucune image attachée", fg="gray")
        
        if self.current_index < len(self.tasks):
            current_task = self.tasks[self.current_index]
            is_block = current_task.get('bloquante', False)
            
            self.lbl_task_name.config(text=f"Étape {current_task['id']} : {current_task['nom']}", fg="black")
            self.lbl_blocking_status.config(text="⚠️ BLOQUANTE en cas d'erreur." if is_block else "ℹ️ Tâche non-bloquante.")
            self.text_short_comment.delete(0, tk.END)
            self.text_long_details.delete("1.0", tk.END)
            self.status_var.set("Succès")
            self.toggle_error_menu()
            
            for item in self.tree.get_children():
                self.tree.item(item, tags=())
            self.tree.item(current_task['id'], tags=('current',))
            self.tree.tag_configure('current', background='#fff9c4')
        else:
            self.trigger_end_state(self.ui_texts["end_success"])

    def validate_task(self):
        current_task = self.tasks[self.current_index]
        task_id = current_task['id']
        task_name = current_task['nom']
        is_blocking = current_task.get('bloquante', False)
        
        short_comment = self.text_short_comment.get().strip()
        long_details = self.text_long_details.get("1.0", tk.END).strip()
        status = self.status_var.get()
        err_level = self.cb_error_level.get() if status == "Erreur" else "-"

        status_text = "✅ Succès" if status == "Succès" else "❌ Échec"
        self.tree.item(task_id, values=(task_id, task_name, "🔴" if is_blocking else "🟢", status_text))

        copied_image_name = None
        if self.attached_image_path and os.path.exists(self.attached_image_path):
            ext = os.path.splitext(self.attached_image_path)[1]
            copied_image_name = f"etape_{task_id}_capture{ext}"
            shutil.copy(self.attached_image_path, os.path.join(self.execution_dir, copied_image_name))

        has_sub_file = bool(long_details) or bool(copied_image_name)
        observation_cell = short_comment if short_comment else "-"
        
        if has_sub_file:
            sub_file_name = f"etape_{task_id}_details.md"
            with open(os.path.join(self.execution_dir, sub_file_name), 'w', encoding='utf-8') as sf:
                sf.write(f"# 🔍 Rapports : {task_name}\n\n[⬅️ Revenir au rapport principal](./rapport_general.md)\n\n")
                if long_details:
                    sf.write(f"### Logs\n```text\n{long_details}\n```\n\n")
                if copied_image_name:
                    sf.write(f"### Preuve\n![Capture](./{copied_image_name})\n\n")
            
            observation_cell = f"[🔍 Détails](./{sub_file_name})" + (f" <br> *{short_comment}*" if short_comment else "")

        with open(self.main_log_file, 'a', encoding='utf-8') as f:
            f.write(f"| {task_id} | {task_name} | {status_text} | {err_level} | {observation_cell} |\n")

        if status == "Erreur" and is_blocking:
            self.tree.item(task_id, tags=('blocked',))
            self.tree.tag_configure('blocked', background='#ffcdd2')
            with open(self.main_log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n🛑 **CRASH PIPELINE :** L'étape {task_id} a échoué.\n")
            
            self.trigger_end_state(self.ui_texts["end_blocked"], is_blocked=True)
            return

        self.current_index += 1
        self.update_ui()

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    app = UltimateFlexibleTrackerApp(root)
    root.mainloop()
