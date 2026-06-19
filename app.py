import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
from datetime import datetime
import os
import shutil

class UltimateTaskTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Orchestrateur de Tâches Pro - V3")
        self.root.geometry("950x650")
        
        self.tasks = []
        self.current_index = 0
        self.yaml_file = None
        self.output_root_dir = None
        self.execution_dir = None
        self.main_log_file = None
        
        # Variables pour l'interface active
        self.attached_image_path = None
        
        self.setup_initial_ui()

    def setup_initial_ui(self):
        """Écran de configuration initiale : choix du YAML et du dossier de sortie."""
        self.welcome_frame = ttk.Frame(self.root, padding=30)
        self.welcome_frame.pack(expand=True, fill=tk.BOTH)
        
        lbl_title = tk.Label(self.welcome_frame, text="🚀 Configuration de l'Orchestrateur", font=("Helvetica", 16, "bold"))
        lbl_title.pack(pady=(0, 20))
        
        # Section Fichier YAML
        yaml_frame = ttk.LabelFrame(self.welcome_frame, text="1. Fichier de Configuration (YAML)", padding=10)
        yaml_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_yaml_status = tk.Label(yaml_frame, text="Aucun fichier YAML sélectionné", fg="red", anchor="w")
        self.lbl_yaml_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        btn_browse_yaml = ttk.Button(yaml_frame, text="Parcourir...", command=self.browse_yaml)
        btn_browse_yaml.pack(side=tk.RIGHT)

        # Section Dossier de Sortie
        out_frame = ttk.LabelFrame(self.welcome_frame, text="2. Répertoire Racine des Rapports (Output)", padding=10)
        out_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_out_status = tk.Label(out_frame, text="Aucun dossier racine sélectionné", fg="red", anchor="w")
        self.lbl_out_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        btn_browse_out = ttk.Button(out_frame, text="Parcourir...", command=self.browse_output_dir)
        btn_browse_out.pack(side=tk.RIGHT)
        
        # Note explicative sur le format ISO
        lbl_iso_info = tk.Label(self.welcome_frame, 
                                text="ℹ️ Un sous-dossier au format ISO (AAAA-MM-JJ_HH-MM-SS) sera créé automatiquement\n"
                                     "dans ce répertoire pour regrouper le rapport général, les fichiers de logs détaillés et les images.", 
                                font=("Helvetica", 9, "italic"), fg="gray", justify="left")
        lbl_iso_info.pack(pady=15, anchor="w")

        # Bouton de lancement
        self.btn_launch = ttk.Button(self.welcome_frame, text="▶️ Initialiser l'Espace de Travail & Lancer", state=tk.DISABLED, command=self.launch_orchestrator)
        self.btn_launch.pack(fill=tk.X, ipady=10, pady=10)

    def browse_yaml(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier YAML des tâches",
            filetypes=[("Fichiers YAML", "*.yml *.yaml"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self.yaml_file = filename
            self.lbl_yaml_status.config(text=os.path.basename(filename), fg="green")
            self.check_ready_to_launch()

    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Sélectionner le répertoire de sortie racine")
        if directory:
            self.output_root_dir = directory
            self.lbl_out_status.config(text=directory, fg="green")
            self.check_ready_to_launch()

    def check_ready_to_launch(self):
        if self.yaml_file and self.output_root_dir:
            self.btn_launch.config(state=tk.NORMAL)

    def launch_orchestrator(self):
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.tasks = data.get('taches', [])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire le fichier YAML :\n{e}")
            return
            
        if not self.tasks:
            messagebox.showwarning("Attention", "Le fichier YAML ne contient aucune tâche valide.")
            return

        # Création du dossier enfant avec l'horodatage
        iso_timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        self.execution_dir = os.path.join(self.output_root_dir, iso_timestamp)
        
        try:
            os.makedirs(self.execution_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer le dossier :\n{e}")
            return
            
        # Fichier principal
        self.main_log_file = os.path.join(self.execution_dir, "rapport_general.md")
        self.init_main_log()

        self.welcome_frame.pack_forget()
        self.setup_main_ui()
        self.update_ui()

    def init_main_log(self):
        with open(self.main_log_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📋 Rapport Général d'Exécution\n\n")
            f.write(f"- **Fichier source :** `{os.path.basename(self.yaml_file)}`\n")
            f.write(f"- **Date :** {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
            f.write(f"- **Dossier d'exécution :** `{self.execution_dir}`\n\n")
            f.write("---\n\n")
            f.write("| ID | Nom de la Tâche | Statut | Criticité | Observations / Fichiers Attachés |\n")
            f.write("| :---: | :--- | :---: | :---: | :--- |\n")

    def setup_main_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        left_frame = ttk.LabelFrame(self.root, text="Timeline", padding=10)
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

        right_frame = ttk.LabelFrame(self.root, text="Action active", padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_task_name = tk.Label(right_frame, text="Tâche : -", font=("Helvetica", 12, "bold"), wraplength=480, justify="left")
        self.lbl_task_name.pack(anchor="w", pady=(0, 2))
        
        self.lbl_blocking_status = tk.Label(right_frame, text="", font=("Helvetica", 9, "italic"))
        self.lbl_blocking_status.pack(anchor="w", pady=(0, 10))

        tk.Label(right_frame, text="✏️ Commentaire court :").pack(anchor="w")
        self.text_short_comment = ttk.Entry(right_frame, width=60)
        self.text_short_comment.pack(fill=tk.X, pady=(0, 10))

        tk.Label(right_frame, text="📝 Logs / Détails étendus (Crée un sous-fichier) :").pack(anchor="w")
        self.text_long_details = tk.Text(right_frame, height=10, width=50, font=("Consolas", 10))
        self.text_long_details.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        img_frame = ttk.Frame(right_frame)
        img_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(img_frame, text="🖼️ Joindre une capture :").pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_img_status = tk.Label(img_frame, text="Aucune image", fg="gray", font=("Helvetica", 9, "italic"))
        self.lbl_img_status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_attach_img = ttk.Button(img_frame, text="Parcourir...", command=self.attach_image)
        btn_attach_img.pack(side=tk.RIGHT)

        control_subframe = ttk.Frame(right_frame)
        control_subframe.pack(fill=tk.X, pady=(0, 15))

        self.status_var = tk.StringVar(value="Succès")
        tk.Radiobutton(control_subframe, text="✅ Succès", variable=self.status_var, value="Succès", font=("Helvetica", 10, "bold"), command=self.toggle_error_menu).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(control_subframe, text="❌ Erreur", variable=self.status_var, value="Erreur", font=("Helvetica", 10, "bold"), command=self.toggle_error_menu).pack(side=tk.LEFT, padx=10)

        self.lbl_error_level = tk.Label(control_subframe, text="Criticité :")
        self.cb_error_level = ttk.Combobox(control_subframe, values=["Faible", "Moyen", "Critique"], state="disabled", width=20)
        self.cb_error_level.set("Moyen")
        self.lbl_error_level.pack(side=tk.LEFT, padx=(20, 5))
        self.cb_error_level.pack(side=tk.LEFT)

        self.btn_validate = ttk.Button(right_frame, text="💾 Valider", command=self.validate_task)
        self.btn_validate.pack(fill=tk.X, ipady=8)

    def attach_image(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif"), ("Tous", "*.*")]
        )
        if filename:
            self.attached_image_path = filename
            self.lbl_img_status.config(text=os.path.basename(filename), fg="green")

    def toggle_error_menu(self):
        if self.status_var.get() == "Erreur":
            self.cb_error_level.config(state="readonly")
        else:
            self.cb_error_level.config(state="disabled")

    def update_ui(self):
        self.attached_image_path = None
        self.lbl_img_status.config(text="Aucune image", fg="gray")
        
        if self.current_index < len(self.tasks):
            current_task = self.tasks[self.current_index]
            is_block = current_task.get('bloquante', False)
            
            self.lbl_task_name.config(text=f"Étape {current_task['id']} : {current_task['nom']}")
            self.lbl_blocking_status.config(text="⚠️ BLOQUANTE en cas d'erreur." if is_block else "ℹ️ Non-bloquante.")
            self.text_short_comment.delete(0, tk.END)
            self.text_long_details.delete("1.0", tk.END)
            self.status_var.set("Succès")
            self.toggle_error_menu()
            
            for item in self.tree.get_children():
                self.tree.item(item, tags=())
            self.tree.item(current_task['id'], tags=('current',))
            self.tree.tag_configure('current', background='#fff9c4')
        else:
            self.lbl_task_name.config(text="🎉 Toutes les tâches sont traitées !")
            self.btn_validate.config(state=tk.DISABLED)
            
            with open(self.main_log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n**Fin :** {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
            messagebox.showinfo("Terminé", f"Processus fini.\nDossier : {self.execution_dir}")

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
                sf.write(f"# 🔍 Détails : {task_name}\n\n[⬅️ Retour](./rapport_general.md)\n\n")
                if long_details:
                    sf.write(f"### Logs\n```text\n{long_details}\n```\n\n")
                if copied_image_name:
                    sf.write(f"### Capture\n![Capture](./{copied_image_name})\n\n")
            
            observation_cell = f"[🔍 Voir détails](./{sub_file_name})" + (f" <br> *{short_comment}*" if short_comment else "")

        with open(self.main_log_file, 'a', encoding='utf-8') as f:
            f.write(f"| {task_id} | {task_name} | {status_text} | {err_level} | {observation_cell} |\n")

        if status == "Erreur" and is_blocking:
            self.tree.item(task_id, tags=('blocked',))
            self.tree.tag_configure('blocked', background='#ffcdd2')
            with open(self.main_log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n🛑 **ARRÊT BLOQUANT :** L'étape {task_id} a échoué.\n")
            messagebox.showerror("BLOCAGE", "Erreur bloquante. Le processus s'arrête.")
            self.btn_validate.config(state=tk.DISABLED)
            return

        self.current_index += 1
        self.update_ui()

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    app = UltimateTaskTrackerApp(root)
    root.mainloop()
