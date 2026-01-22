import os
import sys
import django
from django.conf import settings

# --- Initialize Django ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Determine the module name based on the file's location
# If this file is imported as 'patent_suite.suite_app', use that.
# If run directly, we'll use 'suite_app' but need to ensure it's in sys.path.
MODULE_NAME = 'patent_suite.suite_app' if 'patent_suite' in __name__ else 'suite_app'

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='django-insecure-patent-suite-key-v4',
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[
            MODULE_NAME,
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        },
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        }],
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],
    )
    django.setup()

from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.db import models
from django.shortcuts import render
from django.template import Template, Context

# --- Workspace Manager ---
class WorkspaceManager:
    def __init__(self, base_workspaces_dir=None):
        if base_workspaces_dir is None:
            base_workspaces_dir = os.path.join(BASE_DIR, 'workspaces')
        self.base_dir = base_workspaces_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def init_session_workspace(self, session_id):
        session_dir = os.path.join(self.base_dir, session_id)
        subfolders = ['disclosure', 'references', 'drafts', 'final_export']
        for folder in subfolders:
            folder_path = os.path.join(session_dir, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
        return session_dir

# --- models ---
class CaseFile(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'suite_app'

# --- views ---
def index(request):
    return render_template(INDEX_HTML)

def init_workspace(request):
    session_id = request.GET.get('session_id', 'default_session')
    wm = WorkspaceManager()
    path = wm.init_session_workspace(session_id)
    try:
        CaseFile.objects.get_or_create(session_id=session_id, defaults={'title': 'New Case'})
    except Exception:
        pass
    return JsonResponse({'status': 'success', 'workspace_path': path})

def transcribe(request):
    from patent_suite.utils import transcribe_audio
    if request.method == 'POST':
        # In a real scenario, we'd handle the uploaded file
        # For mock, we'll assume a file was saved
        mock_path = "workspaces/temp_audio.wav"
        text = transcribe_audio(mock_path)
        return JsonResponse({'status': 'success', 'text': text})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# --- Helper for Template Rendering ---
def render_template(template_string, context_dict=None):
    t = Template(template_string)
    c = Context(context_dict or {})
    return HttpResponse(t.render(c))

# --- urls ---
urlpatterns = [
    path('', index, name='index'),
    path('api/init_workspace/', init_workspace, name='init_workspace'),
    path('api/transcribe/', transcribe, name='transcribe'),
    path('api/get_rules/', get_rules, name='get_rules'),
    path('api/update_rules/', update_rules, name='update_rules'),
    path('api/save_config/', save_config, name='save_config'),
    path('api/export_config/', export_config, name='export_config'),
    path('api/illustrate/', generate_illustration_view, name='illustrate'),
]

def export_config(request):
    """
    Zips settings.yaml and the custom_agents/ folder for sharing.
    """
    import zipfile
    import io
    from django.http import HttpResponse

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add settings.yaml
        settings_path = 'patent_suite/settings.yaml'
        if os.path.exists(settings_path):
            zip_file.write(settings_path, arcname='settings.yaml')
        
        # Add custom_agents/ directory
        agents_dir = 'patent_suite/custom_agents'
        if os.path.exists(agents_dir):
            for root, dirs, files in os.walk(agents_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, 'patent_suite')
                    zip_file.write(file_path, arcname=arcname)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="patent_suite_config.zip"'
    return response

def save_config(request):
    """Mock API to save provider credentials and model selections."""
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'Configuration saved successfully (simulated)'})
    return JsonResponse({'status': 'error'}, status=400)

def get_rules(request):
    """Mock API to fetch rules for the editor."""
    from patent_suite.utils.config import ConfigManager
    manager = ConfigManager()
    return JsonResponse(manager.config)

def update_rules(request):
    """Mock API to update rules. In a real app, this would write to settings.yaml."""
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'Rules updated (simulated)'})
    return JsonResponse({'status': 'error'}, status=400)

def generate_illustration_view(request):
    """Local proxy to trigger the IllustratorAgent."""
    from patent_suite.agents.illustrator import IllustratorAgent
    
    # Simple hardcoded context for the demo
    # In a real app, this would come from the current editor content
    claims_text = request.GET.get('claims', 'A holographic bread slicing apparatus comprising a laser array.')
    
    agent = IllustratorAgent()
    result = agent.run("Generate illustration", {"claims_text": claims_text})
    return JsonResponse(result)

# --- templates ---
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patent Suite | Senior AI Attorney</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        :root {
            --bg: #0d1117;
            --surface: rgba(22, 27, 34, 0.7);
            --card: rgba(48, 54, 61, 0.4);
            --accent: #58a6ff;
            --text-main: #c9d1d9;
            --text-muted: #8b949e;
            --border: #30363d;
            --glass: rgba(255, 255, 255, 0.03);
        }
        
        * { box-sizing: border-box; }
        
        body {
            background: var(--bg);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            margin: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
            background-image: radial-gradient(circle at 50% -20%, #1e293b, #0d1117);
        }

        /* --- Header / Navigation --- */
        .sidebar-nav {
            width: 64px;
            background: var(--surface);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px 0;
            backdrop-filter: blur(10px);
            z-index: 100;
        }
        
        .nav-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: var(--accent);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 14px;
            cursor: pointer;
        }

        .settings-btn {
            margin-top: auto;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 20px;
            transition: color 0.2s;
        }
        
        .settings-btn:hover { color: var(--accent); }

        /* --- Main Layout --- */
        .main-container {
            flex: 1;
            display: flex;
            width: 100%;
            overflow: hidden;
            position: relative;
        }

        .pane {
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
            background: rgba(13, 17, 23, 0.3);
            backdrop-filter: blur(5px);
        }

        .resizer {
            width: 4px;
            cursor: col-resize;
            background: rgba(88, 166, 255, 0.05);
            transition: background 0.2s;
            z-index: 10;
        }

        .resizer:hover {
            background: var(--accent);
        }

        /* Zone A: Case Files */
        #zone-a {
            width: 20%;
            min-width: 150px;
            border-right: 1px solid var(--border);
        }

        /* Zone B: Workspace */
        #zone-b {
            flex: 1;
            min-width: 300px;
            background: transparent;
        }

        /* Zone C: Agent HUD */
        #zone-c {
            width: 30%;
            min-width: 200px;
            border-left: 1px solid var(--border);
            background: rgba(13, 17, 23, 0.6);
        }

        /* --- Components --- */
        .pane-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(12px);
            background: var(--surface);
        }

        .pane-header h2 {
            margin: 0;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            font-weight: 600;
        }

        .content-scroll {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
        }

        /* --- Cards & Skeletal UI --- */
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            backdrop-filter: blur(4px);
            transition: transform 0.2s, border-color 0.2s;
        }
        
        .card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }

        .card h4 {
            margin: 0 0 8px 0;
            color: var(--accent);
            font-size: 16px;
        }

        .card p {
            margin: 0;
            font-size: 13px;
            line-height: 1.5;
            color: var(--text-muted);
        }

        .skeleton {
            height: 14px;
            background: linear-gradient(90deg, #161b22 25%, #21262d 50%, #161b22 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            border-radius: 4px;
            margin-bottom: 12px;
        }

        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        /* --- Editor --- */
        .editor-container {
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        .draft-editor {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-main);
            padding: 32px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            line-height: 1.8;
            resize: none;
            outline: none;
        }

        .btn-premium {
            background: var(--accent);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-premium:hover { opacity: 0.9; }

        /* --- Comparison Mode Styles --- */
        .comparison-btn {
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent);
            border: 1px solid rgba(88, 166, 255, 0.3);
            margin-left: auto;
        }
        
        .clause-item {
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            display: block;
            margin-bottom: 2px;
        }
        
        .clause-item:hover {
            background: rgba(88, 166, 255, 0.15);
            color: var(--accent);
        }
        
        .clause-item.novel {
            border-left: 3px solid #34a853;
            background: rgba(52, 168, 83, 0.05);
        }
        
        .clause-item.novel:hover {
            background: rgba(52, 168, 83, 0.15);
            color: #34a853;
        }

        .prior-art-highlight {
            background: rgba(88, 166, 255, 0.2) !important;
            border-color: var(--accent) !important;
            box-shadow: 0 0 15px rgba(88, 166, 255, 0.2);
        }

        .connection-line {
            position: absolute;
            height: 2px;
            background: var(--accent);
            opacity: 0.3;
            pointer-events: none;
            z-index: 100;
            transition: all 0.2s;
        }

        /* --- Modal Styles --- */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(8px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            width: 800px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }

        .modal-header {
            padding: 24px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-tabs {
            display: flex;
            background: rgba(0,0,0,0.2);
            padding: 0 24px;
        }

        .tab-btn {
            padding: 16px 24px;
            color: var(--text-muted);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 2px solid transparent;
        }

        .tab-btn.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }

        .modal-body {
            flex: 1;
            padding: 32px;
            overflow-y: auto;
        }

        .rule-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .rule-info { flex: 1; }
        .rule-info h4 { margin: 0 0 4px 0; font-size: 14px; color: var(--text-main); }
        .rule-info p { margin: 0; font-size: 12px; color: var(--text-muted); line-height: 1.4; }

        .rule-actions {
            display: flex;
            gap: 12px;
            align-items: center;
            margin-left: 20px;
        }

        /* Toggle Switch */
        .switch {
            position: relative;
            display: inline-block;
            width: 40px;
            height: 20px;
        }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #333;
            transition: .4s;
            border-radius: 20px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 14px; width: 14px;
            left: 3px; bottom: 3px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider { background-color: var(--accent); }
        input:checked + .slider:before { transform: translateX(20px); }

        /* Intervention Button */
        .stop-button {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: #ea4335;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 30px;
            box-shadow: 0 4px 15px rgba(234, 67, 53, 0.4);
            cursor: pointer;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .stop-button:hover {
            transform: translateX(-50%) translateY(-2px);
            box-shadow: 0 6px 20px rgba(234, 67, 53, 0.5);
            background: #d93025;
        }

        /* Intervention Overlay */
        .intervention-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(13, 17, 23, 0.95);
            backdrop-filter: blur(15px);
            z-index: 2000;
            display: none;
            align-items: center;
            justify-content: center;
        }
        .intervention-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 40px;
            width: 500px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            animation: slideUp 0.3s ease-out;
        }
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .intervention-option {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
            font-size: 14px;
            color: var(--text-main);
            display: block;
            width: 100%;
        }
        .intervention-option:hover {
            border-color: var(--accent);
            background: rgba(88, 166, 255, 0.1);
            transform: translateX(5px);
        }

        /* Toggle Switch */
        .switch {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 22px;
        }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #334155;
            transition: .4s;
            border-radius: 22px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 16px; width: 16px;
            left: 3px; bottom: 3px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider { background-color: var(--accent); }
        input:checked + .slider:before { transform: translateX(22px); }

        .form-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        /* Form Styles */
        .form-group {
            margin-bottom: 24px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            color: var(--text-muted);
        }
        .form-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            color: var(--text-main);
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        .form-input:focus {
            border-color: var(--accent);
        }

        /* Visualization Tree Styles */
        #patent-tree-container {
            width: 100%;
            height: 100%;
            display: none;
            background: rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
            flex-direction: column;
        }
        .node circle {
            fill: var(--surface);
            stroke: var(--accent);
            stroke-width: 2px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .node.orphan circle {
            stroke: #ea4335;
            fill: rgba(234, 67, 53, 0.1);
        }
        .node text {
            font-size: 11px;
            fill: var(--text-main);
            font-family: 'Inter', sans-serif;
            pointer-events: none;
        }
        .link {
            fill: none;
            stroke: var(--border);
            stroke-width: 1.5px;
            opacity: 0.5;
        }
        .link.orphan {
            stroke: #ea4335;
            opacity: 0.8;
        }
        .node:hover circle {
            filter: brightness(1.2);
            stroke-width: 3px;
        }

        /* Stepper Styles */
        .stepper {
            display: flex;
            flex-direction: column;
            gap: 0;
            padding-left: 10px;
        }
        .step {
            display: flex;
            gap: 16px;
            position: relative;
            padding-bottom: 24px;
        }
        .step:not(:last-child)::after {
            content: '';
            position: absolute;
            left: 11px;
            top: 24px;
            bottom: 0;
            width: 2px;
            background: var(--border);
            opacity: 0.5;
        }
        .step-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: var(--bg);
            border: 2px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            z-index: 1;
            flex-shrink: 0;
            transition: all 0.3s;
        }
        .step.done .step-icon { border-color: #34a853; color: #34a853; background: rgba(52, 168, 83, 0.1); }
        .step.active .step-icon { border-color: var(--accent); color: var(--accent); box-shadow: 0 0 10px rgba(88, 166, 255, 0.3); }
        .step-content { flex: 1; padding-top: 3px; }
        .step-title { font-size: 13px; font-weight: 600; color: var(--text-main); margin-bottom: 4px; }
        .step-desc { font-size: 12px; color: var(--text-muted); line-height: 1.4; }
        
        .thought-log {
            margin-top: 12px;
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-muted);
            display: none;
            overflow-x: auto;
        }
        .toggle-thoughts {
            font-size: 11px;
            color: var(--accent);
            cursor: pointer;
            margin-top: 8px;
            display: inline-block;
            text-decoration: underline;
        }

        /* Persona Badges */
        .persona-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.3s;
        }
        .mode-planning { background: rgba(142, 68, 173, 0.1); color: #9b59b6; border: 1px solid rgba(142, 68, 173, 0.3); }
        .mode-research { background: rgba(52, 152, 219, 0.1); color: #3498db; border: 1px solid rgba(52, 152, 219, 0.3); }
        .mode-adversarial { background: rgba(231, 76, 60, 0.1); color: #e74c3c; border: 1px solid rgba(231, 76, 60, 0.3); }
        .mode-custom { background: rgba(243, 156, 18, 0.1); color: #f39c12; border: 1px solid rgba(243, 156, 18, 0.3); }

        /* Editor Layout */
        #monaco-editor, #monaco-diff-editor {
            flex: 1;
            width: 100%;
            height: 100%;
        }
        #monaco-diff-editor {
            display: none;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 10px;
        }

        /* Agent Loader */
        .drop-zone {
            border: 2px dashed var(--border);
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            color: var(--text-muted);
            transition: all 0.3s;
            background: rgba(255, 255, 255, 0.02);
            cursor: pointer;
            margin-top: 24px;
        }
        .drop-zone.dragover {
            border-color: var(--accent);
            background: rgba(88, 166, 255, 0.05);
            color: var(--accent);
        }
        .agent-detected-card {
            background: var(--card);
            border: 1px solid var(--accent);
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            animation: fadeIn 0.3s ease-out;
            text-align: left;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="sidebar-nav">
        <div class="nav-icon">P</div>
        <div class="settings-btn" id="open-settings">⚙️</div>
    </div>

    <!-- Settings Modal -->
    <div class="modal-overlay" id="settings-modal">
        <div class="modal">
            <div class="modal-header">
                <h3 style="margin:0; font-size: 18px;">Preferences</h3>
                <button class="btn-premium" onclick="closeSettings()" style="padding: 6px 12px;">Close</button>
            </div>
            <div class="modal-tabs">
                <div class="tab-btn active" onclick="switchTab(this, 'rules')">Agent Rules</div>
                <div class="tab-btn" onclick="switchTab(this, 'export')">Export Settings</div>
                <div class="tab-btn" onclick="switchTab(this, 'advanced')">Advanced</div>
                <div class="tab-btn" onclick="switchTab(this, 'premium')" style="color: #fbbf24;">✨ Premium / Cloud</div>
            </div>
            <div class="modal-body" id="settings-body">
                <div id="rules-tab-content">
                    <div id="rules-editor-container"></div>
                </div>
                <div id="export-tab-content" style="display:none;">
                    <h5 style="margin: 0 0 16px 0; color:var(--text-muted); font-size: 11px; text-transform: uppercase;">Jurisdiction & Office</h5>
                    <div class="form-group">
                        <label>Patent Office (Format Enforcement)</label>
                        <select class="form-input" id="jurisdiction-select">
                            <option value="USPTO">USPTO (United States)</option>
                            <option value="EPO">EPO (Europe - Two-Part Claims)</option>
                            <option value="WIPO">WIPO (International - PCT Stage)</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-top: 32px; padding: 20px; background: rgba(0, 195, 255, 0.05); border: 1px dashed var(--accent); border-radius: 12px;">
                        <h6 style="margin: 0 0 8px 0; color: var(--accent);">Firm-Wide Synchronization</h6>
                        <p style="color:var(--text-muted); font-size: 12px; margin-bottom: 16px;">
                            Export your custom rules, provider models, and specialized agents into a bundle to share with your team.
                        </p>
                        <button class="btn-premium" onclick="downloadConfig()" style="width: 100%; padding: 10px;">
                            <i class="fas fa-download" style="margin-right: 8px;"></i> Download Setup Bundle (.zip)
                        </button>
                    </div>
                    <div style="margin-top: 24px;">
                        <p style="color:var(--text-muted); font-size: 13px;">Advanced export features (watermarking, headers) coming soon.</p>
                    </div>
                </div>
                <div id="advanced-tab-content" style="display:none;">
                    <h5 style="margin: 0 0 16px 0; color:var(--text-muted); font-size: 11px; text-transform: uppercase;">Provider Configuration</h5>
                    <div class="form-group">
                        <label>OpenAI API Key</label>
                        <input type="password" class="form-input" placeholder="sk-..." value="••••••••••••••••">
                    </div>
                    <div class="form-group">
                        <label>Anthropic API Key</label>
                        <input type="password" class="form-input" placeholder="sk-ant-...">
                    </div>
                    <div class="form-group">
                        <label>Google Gemini API Key</label>
                        <input type="password" class="form-input" placeholder="AIza...">
                    </div>
                    
                    <h5 style="margin: 24px 0 16px 0; color:var(--text-muted); font-size: 11px; text-transform: uppercase;">Model Selection</h5>
                    <div class="form-group">
                        <label>Orchestrator (Planning & Reasoning)</label>
                        <select class="form-input">
                            <option>GPT-4o (OpenAI)</option>
                            <option>Claude 3.5 Sonnet (Anthropic)</option>
                            <option>Gemini 1.5 Pro (Google)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Sub-Agents (Drafting & Retrieval)</label>
                        <select class="form-input">
                            <option>GPT-4o-mini (OpenAI)</option>
                            <option>Claude 3 Haiku (Anthropic)</option>
                            <option>Gemini 1.5 Flash (Google)</option>
                        </select>
                    </div>

                    <h5 style="margin: 24px 0 16px 0; color:var(--text-muted); font-size: 11px; text-transform: uppercase;">Custom Agent Plugin</h5>
                    <div id="agent-drop-zone" class="drop-zone">
                        <div id="drop-zone-content">
                            <div style="font-size: 24px; margin-bottom: 8px;">📁</div>
                            <div style="font-size: 13px; font-weight: 600; color: var(--text-main);">Drop Agent Script (.py)</div>
                            <div style="font-size: 11px; margin-top: 4px;">Must inherit from BaseAgent</div>
                        </div>
                    </div>
                    <div id="detected-agent-container"></div>

                    <button class="btn-premium" onclick="saveAdvancedSettings()" style="width: 100%; padding: 12px; margin-top: 32px;">Save Preferences</button>
                    <p id="save-status" style="text-align:center; font-size: 12px; color: var(--accent); margin-top: 12px; display:none;">Settings Saved!</p>
                </div>
                <div id="premium-tab-content" style="display:none;">
                    <h5 style="margin: 0 0 16px 0; color:#fbbf24; font-size: 11px; text-transform: uppercase;">Cloud Hybrid Configuration</h5>
                    <div class="form-group">
                        <label>OpenPatent Cloud API Key</label>
                        <input type="password" id="cloud-api-key" class="form-input" placeholder="op-..." oninput="validatePremiumKey()">
                    </div>
                    <div class="form-row">
                        <label style="font-size: 13px; color: var(--text-main);">Use Cloud Agents where available?</label>
                        <label class="switch">
                            <input type="checkbox" id="use-cloud-agents">
                            <span class="slider"></span>
                        </label>
                    </div>
                    
                    <div id="premium-features-locked" style="margin-top: 32px; padding: 24px; border: 1px solid #334155; border-radius: 12px; text-align: center; background: rgba(251, 191, 36, 0.05);">
                        <div style="font-size: 24px; margin-bottom: 12px;">🔒</div>
                        <h4 style="margin: 0 0 8px 0; color: #fbbf24;">Premium Agents Locked</h4>
                        <p style="font-size: 12px; color: var(--text-muted);">Enter your 12-digit OpenPatent Cloud API key to unlock adversarial examiners and specialized retrieval agents.</p>
                    </div>
                    
                    <div id="premium-features-unlocked" style="display:none; margin-top: 32px; padding: 24px; border: 1px solid #34d399; border-radius: 12px; text-align: center; background: rgba(52, 211, 153, 0.05);">
                        <div style="font-size: 24px; margin-bottom: 12px;">✅</div>
                        <h4 style="margin: 0 0 8px 0; color: #34d399;">Cloud Agents Unlocked</h4>
                        <p style="font-size: 12px; color: var(--text-muted);">Hybrid mode active. The system will now route complex legal queries through OpenPatent Cloud.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="main-container" id="main-layout">
        <!-- Zone A: Case Files -->
        <div class="pane" id="zone-a">
            <div class="pane-header">
                <h2>Case Files</h2>
                <span style="font-size: 10px; color: var(--text-muted); cursor: pointer;">📂 New</span>
            </div>
            <div class="content-scroll" id="file-explorer" style="padding: 12px;">
                <div style="font-size: 12px; color: var(--text-muted); padding: 8px 12px; background: rgba(88, 166, 255, 0.1); border-radius: 6px; margin-bottom: 8px;">
                    📁 disclosure/
                </div>
                <div style="font-size: 13px; color: var(--text-main); padding: 4px 24px;">📄 notes.txt</div>
                <div style="font-size: 13px; color: var(--text-main); padding: 4px 24px;">📄 meta.json</div>
                
                <div style="font-size: 12px; color: var(--text-muted); padding: 8px 12px; margin-top: 12px;">
                    📁 references/
                </div>
                <div style="font-size: 13px; color: var(--text-main); padding: 4px 24px; color: var(--accent);">📄 US-1111111-B2.pdf</div>
                <div style="font-size: 13px; color: var(--text-main); padding: 4px 24px;">📄 JP-2023001-A.pdf</div>
                
                <div style="font-size: 12px; color: var(--text-muted); padding: 8px 12px; margin-top: 12px;">
                    📁 drafts/
                </div>
                <div style="font-size: 13px; color: var(--text-main); padding: 4px 24px;">📄 draft_v1.docx</div>
            </div>
        </div>

        <div class="resizer" id="resizer-1"></div>

        <!-- Zone B: Workspace -->
        <div class="pane" id="zone-b">
            <div class="pane-header">
                <h2>Document Workspace</h2>
                <div style="display: flex; gap: 12px; align-items: center;">
                    <button class="btn-premium comparison-btn" id="toggle-visual-tree">Visual Tree</button>
                    <button class="btn-premium comparison-btn" id="toggle-compare">Split View</button>
                    <button class="btn-premium" id="run-illustrator-btn">🎨 Illustrate</button>
                    <button class="btn-premium">Export</button>
                </div>
            </div>
            <div class="editor-container" id="workspace-view-container" style="flex:1; display:flex; flex-direction:column; overflow:hidden;">
                <div id="monaco-editor-wrapper" style="flex: 1; display: flex; flex-direction: column;">
                    <div id="editor-toolbar" style="padding: 10px 32px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid var(--border);">
                        <button id="mic-btn" class="btn-premium" style="background: #ea4335; width: 34px; height: 34px; border-radius: 50%; padding: 0; justify-content: center; font-size: 12px;">
                            🎤
                        </button>
                        <span id="mic-status" style="font-size: 11px; color: var(--text-muted);">Voice Command Active</span>
                    </div>
                    <!-- Risk Score Dashboard -->
                    <div style="padding: 8px 32px; background: rgba(0,0,0,0.2); border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 15px;">
                        <div id="risk-traffic-light" style="display: flex; gap: 6px;">
                            <div id="light-red" style="width: 10px; height: 10px; border-radius: 50%; background: #331111;"></div>
                            <div id="light-yellow" style="width: 10px; height: 10px; border-radius: 50%; background: #333311;"></div>
                            <div id="light-green" style="width: 10px; height: 10px; border-radius: 50%; background: #113311;"></div>
                        </div>
                        <span id="risk-summary" style="font-size: 11px; color: var(--text-muted);">Legal Audit Clean</span>
                    </div>
                    <div id="comparison-view" class="content-scroll" style="display: none; background: rgba(0,0,0,0.1); font-family: 'JetBrains Mono', monospace;">
                        <!-- Split view logic here -->
                    </div>
                    <div id="monaco-editor"></div>
                    <div id="monaco-diff-editor"></div>
                </div>
                
                <div id="patent-tree-container">
                    <div style="padding: 15px 32px; border-bottom: 1px solid var(--border); background: var(--surface); display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 11px; color: var(--text-muted);">Legal Claim Hierarchy Graph</span>
                        <div id="tree-legend" style="display:flex; gap: 15px;">
                            <div style="display:flex; align-items:center; gap: 6px; font-size: 10px;"><div style="width: 8px; height: 8px; border-radius: 50%; background: var(--accent);"></div> Valid</div>
                            <div style="display:flex; align-items:center; gap: 6px; font-size: 10px;"><div style="width: 8px; height: 8px; border-radius: 50%; background: #ea4335;"></div> Orphaned</div>
                        </div>
                    </div>
                    <div id="tree-canvas" style="flex: 1; overflow: hidden;"></div>
                </div>
            </div>
        </div>

        <div class="resizer" id="resizer-2"></div>

        <div class="pane" id="zone-c">
            <div class="pane-header">
                <h2>OODA HUD</h2>
                <div id="active-persona" class="persona-badge mode-planning">
                    <span id="persona-icon">🧠</span>
                    <span id="persona-name">Orchestration Mode</span>
                </div>
            </div>
            <div class="content-scroll" id="agent-hud" style="padding: 24px;">
                <div class="stepper">
                    <div class="step done" id="step-planning">
                        <div class="step-icon">✓</div>
                        <div class="step-content">
                            <div class="step-title">Observe & Orient (Planning)</div>
                            <div class="step-desc">Orchestrator identified 4 drafting sub-tasks and 2 search queries.</div>
                            <span class="toggle-thoughts" onclick="toggleThoughts('thoughts-planning')">Debug Thoughts</span>
                            <div class="thought-log" id="thoughts-planning">
                                {
                                  "agent": "Orchestrator",
                                  "strategy": "Hierarchical Decomposition",
                                  "tokens": 450,
                                  "reasoning": "Invention involves directed energy food processing. Strategy: 1. Prior Art Search (US Patents), 2. Claim Construction (Method/System), 3. Antecedent Check."
                                }
                            </div>
                        </div>
                    </div>

                    <div class="step active" id="step-searching">
                        <div class="step-icon">⋯</div>
                        <div class="step-content">
                            <div class="step-title">Decide (Searching)</div>
                            <div class="step-desc">Searcher Agent retrieving prior art from USPTO Bulk API...</div>
                        </div>
                    </div>

                    <div class="step pending" id="step-drafting">
                        <div class="step-icon"></div>
                        <div class="step-content">
                            <div class="step-title">Act (Drafting)</div>
                            <div class="step-desc">Drafter Agent waiting for search results.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Intervention UI -->
    <button class="stop-button" id="stop-paddle" onclick="triggerIntervention()">
        <span>🛑</span> STOP & REDIRECT
    </button>

    <div class="intervention-overlay" id="intervention-overlay">
        <div class="intervention-card">
            <h2 style="margin: 0 0 15px 0; font-size: 24px;">AI Paused</h2>
            <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 30px;">
                Why are you stopping me? Provide steering to redirect the workflow.
            </p>
            
            <button class="intervention-option" onclick="redirectAI('Wrong direction')">
                <strong>🔄 Wrong Direction</strong>
                <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Restart the current step with a new strategy.</div>
            </button>
            
            <button class="intervention-option" onclick="redirectAI('Too broad')">
                <strong>⚖️ Too Broad</strong>
                <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Narrow down the scope to specific disclosure details.</div>
            </button>
            
            <button class="intervention-option" onclick="redirectAI('Add this detail')">
                <strong>📝 Add This Detail</strong>
                <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Inject a missed claim limitation or invention feature.</div>
            </button>

            <textarea class="form-input" id="custom-steering" placeholder="Custom instructions..." style="margin-top: 20px; min-height: 80px;"></textarea>
            
            <div style="display:flex; gap: 12px; margin-top: 24px;">
                <button class="btn-premium" onclick="redirectAI('Custom')" style="flex:1; padding:12px;">Resume with Redirect</button>
                <button class="btn-premium" onclick="closeIntervention()" style="background:transparent; border:1px solid var(--border); padding:12px;">Cancel</button>
            </div>
        </div>
    </div>

    <!-- Simulation Overlay -->
    <div class="intervention-overlay" id="simulation-overlay">
        <div class="intervention-card" style="width: 600px;">
            <h2 style="margin: 0 0 15px 0; font-size: 24px;">Rule Simulation</h2>
            <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">
                Verifying how the selected rule affects the agent's prompt pattern.
            </p>
            
            <div style="background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 12px; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 11px;">
                <div style="color: var(--accent); margin-bottom: 8px;"># Raw Prompt Segment:</div>
                <div style="color: var(--text-muted); line-height: 1.6;" id="sim-input">Loading simulation...</div>
                
                <div style="height: 1px; background: var(--border); margin: 20px 0;"></div>
                
                <div style="color: #34a853; margin-bottom: 8px;"># Processed Output (Rule Applied):</div>
                <div style="color: var(--text-main); line-height: 1.6;" id="sim-output">Processing rules...</div>
            </div>
            
            <div style="display:flex; justify-content: flex-end; margin-top: 24px;">
                <button class="btn-premium" onclick="document.getElementById('simulation-overlay').style.display = 'none'" style="padding:12px 24px;">Close Simulation</button>
            </div>
        </div>
    </div>

    <script>
        let editor;
        let diffEditor;
        let mediaRecorder;
        let audioChunks = [];
        const micBtn = document.getElementById('mic-btn');
        const micStatus = document.getElementById('mic-status');

        const BANNED_WORDS = {
            'approximately': { risk: 'Section 112 Indefiniteness', replacement: 'within a range of', warning: 'Term lacks a specific objective boundary.' },
            'basically': { risk: 'Superfluous/Vague', replacement: '', warning: 'Weakens claim precision. Suggest removing.' },
            'substantial': { risk: 'Indefinite Degree', replacement: 'at least 80%', warning: 'May be rejected unless defined by a specific percentage or range.' },
            'very': { risk: 'Relative Term', replacement: '', warning: 'Lacks objective comparison. Use absolute technical values instead.' },
            'about': { risk: 'Section 112 Indefiniteness', replacement: 'within 10% of', warning: 'Commonly rejected as indefinite without numerical context.' }
        };

        /* --- Monaco Editor Initialization --- */
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});
        require(['vs/editor/editor.main'], function() {
            // Define Patent Language
            monaco.languages.register({ id: 'patent' });
            monaco.languages.setMonarchTokensProvider('patent', {
                keywords: ['comprising', 'consisting', 'said', 'plurality', 'wherein', 'characterized', 'claim', 'method', 'system'],
                tokenizer: {
                    root: [
                        [/[a-zA-Z_$][\w$]*/, {
                            cases: {
                                '@keywords': 'keyword',
                                '@default': 'identifier'
                            }
                        }],
                        [/\[CLAIMS\]|\[FIELD OF THE INVENTION\]/, 'type'],
                        [/\d+\./, 'number'],
                    ]
                }
            });

            // Set Theme
            monaco.editor.defineTheme('patentDark', {
                base: 'vs-dark',
                inherit: true,
                rules: [
                    { token: 'keyword', foreground: '58a6ff', fontStyle: 'bold' },
                    { token: 'type', foreground: 'f39c12' },
                    { token: 'identifier', foreground: 'c9d1d9' }
                ],
                colors: {
                    'editor.background': '#0d111700'
                }
            });

            editor = monaco.editor.create(document.getElementById('monaco-editor'), {
                value: 'Initializing patent drafting agents...',
                language: 'patent',
                theme: 'patentDark',
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                readOnly: false,
                automaticLayout: true,
                fontFamily: 'JetBrains Mono',
                fontSize: 14,
                minimap: { enabled: false },
                wordWrap: 'on'
            });

            diffEditor = monaco.editor.createDiffEditor(document.getElementById('monaco-diff-editor'), {
                theme: 'patentDark',
                lineNumbers: 'on',
                fontSize: 14,
                fontFamily: 'JetBrains Mono',
                automaticLayout: true,
                readOnly: true,
                renderSideBySide: true
            });

            // Register Linter (Diagnostics)
            editor.onDidChangeModelContent(() => {
                debounce(runLinter, 500)();
            });

            // Illustrator Logic
            document.getElementById('run-illustrator-btn').onclick = async () => {
                const btn = document.getElementById('run-illustrator-btn');
                const container = document.getElementById('illustration-container');
                const viewport = document.getElementById('illustration-viewport');
                const claims = editor.getValue();

                btn.innerText = '✨ Generating...';
                btn.disabled = true;
                container.style.display = 'block';
                viewport.innerHTML = '<div class="skeleton" style="width: 100%; height: 300px; margin: 0;"></div>';

                try {
                    const res = await fetch(`/api/illustrate/?claims=${encodeURIComponent(claims)}`);
                    const data = await res.json();
                    
                    if (data.status === 'success') {
                        viewport.innerHTML = `<img src="${data.image_url}" alt="Patent Illustration" style="max-width: 100%; height: auto;">`;
                    } else {
                        viewport.innerHTML = `<p style="color: #ea4335; font-size: 12px; padding: 20px;">Error: ${data.message}</p>`;
                    }
                } catch (e) {
                    viewport.innerHTML = `<p style="color: #ea4335; font-size: 12px; padding: 20px;">Service unavailable.</p>`;
                } finally {
                    btn.innerText = '🎨 Illustrate';
                    btn.disabled = false;
                }
            };

            // Register Hover Provider
            monaco.languages.registerHoverProvider('patent', {
                provideHover: function(model, position) {
                    const word = model.getWordAtPosition(position);
                    if (!word) return null;
                    
                    const banned = BANNED_WORDS[word.word.toLowerCase()];
                    if (banned) {
                        return {
                            range: new monaco.Range(position.lineNumber, word.startColumn, position.lineNumber, word.endColumn),
                            contents: [
                                { value: `**⚠️ Legal Risk: ${banned.risk}**` },
                                { value: `*Warning:* ${banned.warning}` },
                                { value: banned.replacement ? `**Suggestion:** Replace with '${banned.replacement}'` : `**Suggestion:** Remove the term.` },
                                { value: `[Section 112 Compliance Engine]` }
                            ]
                        };
                    }
                    return null;
                }
            });

            // Primary run
            runLinter();
        });

        let linterTimeout;
        function debounce(func, wait) {
            return function() {
                clearTimeout(linterTimeout);
                linterTimeout = setTimeout(func, wait);
            };
        }

        function runLinter() {
            if (!editor) return;
            const model = editor.getModel();
            const markers = [];
            const text = model.getValue();

            Object.keys(BANNED_WORDS).forEach(banned => {
                const regex = new RegExp(`\\b${banned}\\b`, 'gi');
                let match;
                while ((match = regex.exec(text)) !== null) {
                    const startPos = model.getPositionAt(match.index);
                    const endPos = model.getPositionAt(match.index + match[0].length);
                    
                    markers.push({
                        severity: monaco.MarkerSeverity.Warning,
                        message: `Risk Warning: ${BANNED_WORDS[banned].risk}. ${BANNED_WORDS[banned].warning}`,
                        startLineNumber: startPos.lineNumber,
                        startColumn: startPos.column,
                        endLineNumber: endPos.lineNumber,
                        endColumn: endPos.column
                    });
                }
            });

            monaco.editor.setModelMarkers(model, 'linter', markers);
            
            // Update HUD Risk Score if needed
            updateRiskScore(text, markers.length > 0, false, false);
        }

        function setEditorReadOnly(locked) {
            if (editor) {
                editor.updateOptions({ readOnly: locked });
            }
        }

        const openSettingsBtn = document.getElementById('open-settings');
        const settingsModal = document.getElementById('settings-modal');
        const rulesContainer = document.getElementById('rules-editor-container');
        const settingsBody = document.getElementById('settings-body');

        openSettingsBtn.onclick = async () => {
            settingsModal.style.display = 'flex';
            await loadRules();
        };

        function closeSettings() {
            settingsModal.style.display = 'none';
        }

        function switchTab(btn, tabId) {
            // Update Tab Buttons
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update Content
            document.getElementById('rules-tab-content').style.display = tabId === 'rules' ? 'block' : 'none';
            document.getElementById('export-tab-content').style.display = tabId === 'export' ? 'block' : 'none';
            document.getElementById('advanced-tab-content').style.display = tabId === 'advanced' ? 'block' : 'none';
            document.getElementById('premium-tab-content').style.display = tabId === 'premium' ? 'block' : 'none';
        }

        function validatePremiumKey() {
            const key = document.getElementById('cloud-api-key').value;
            const lockedView = document.getElementById('premium-features-locked');
            const unlockedView = document.getElementById('premium-features-unlocked');
            
            // Simple validation logic for demo: key must start with 'op-' and be longer than 10 chars
            if (key.startsWith('op-') && key.length > 10) {
                lockedView.style.display = 'none';
                unlockedView.style.display = 'block';
            } else {
                lockedView.style.display = 'block';
                unlockedView.style.display = 'none';
            }
        }

        async function saveAdvancedSettings() {
            const status = document.getElementById('save-status');
            status.style.display = 'block';
            await fetch('/api/save_config/', { method: 'POST' });
            setTimeout(() => { status.style.display = 'none'; }, 2000);
        }

        function downloadConfig() {
            window.location.href = '/api/export_config/';
        }

        /* --- Resizable Pane Logic --- */
        const resizer1 = document.getElementById('resizer-1');
        const resizer2 = document.getElementById('resizer-2');
        const zoneA = document.getElementById('zone-a');
        const zoneB = document.getElementById('zone-b');
        const zoneC = document.getElementById('zone-c');
        const mainLayout = document.getElementById('main-layout');

        function initResizer(resizer, paneBefore, paneAfter, isLeft) {
            let x = 0;
            let wBefore = 0;
            let wAfter = 0;

            const mouseDownHandler = function(e) {
                x = e.clientX;
                const rectBefore = paneBefore.getBoundingClientRect();
                const rectAfter = paneAfter.getBoundingClientRect();
                wBefore = rectBefore.width;
                wAfter = rectAfter.width;

                document.addEventListener('mousemove', mouseMoveHandler);
                document.addEventListener('mouseup', mouseUpHandler);
                resizer.style.background = 'var(--accent)';
            };

            const mouseMoveHandler = function(e) {
                const dx = e.clientX - x;
                const totalWidth = mainLayout.getBoundingClientRect().width;
                
                if (isLeft) {
                    const newW = wBefore + dx;
                    if (newW > 150 && newW < totalWidth * 0.4) {
                        paneBefore.style.width = `${newW}px`;
                        paneBefore.style.flex = 'none';
                    }
                } else {
                    const newW = wAfter - dx;
                    if (newW > 200 && newW < totalWidth * 0.4) {
                        paneAfter.style.width = `${newW}px`;
                        paneAfter.style.flex = 'none';
                    }
                }
            };

            const mouseUpHandler = function() {
                document.removeEventListener('mousemove', mouseMoveHandler);
                document.removeEventListener('mouseup', mouseUpHandler);
                resizer.style.background = '';
            };

            resizer.addEventListener('mousedown', mouseDownHandler);
        }

        initResizer(resizer1, zoneA, zoneB, true);
        initResizer(resizer2, zoneB, zoneC, false);

        function toggleThoughts(id) {
            const el = document.getElementById(id);
            el.style.display = el.style.display === 'block' ? 'none' : 'block';
        }

        function setActivePersona(mode, name, icon) {
            const badge = document.getElementById('active-persona');
            const nameEl = document.getElementById('persona-name');
            const iconEl = document.getElementById('persona-icon');
            
            badge.className = `persona-badge mode-${mode}`;
            nameEl.innerText = name;
            iconEl.innerText = icon;
        }

        /* --- Intervention Logic --- */
        function triggerIntervention() {
            document.getElementById('intervention-overlay').style.display = 'flex';
            // In a real app, this would send a 'pause' command to the backend socket
            if (editor) editor.updateOptions({ readOnly: true }); 
        }

        function closeIntervention() {
            document.getElementById('intervention-overlay').style.display = 'none';
        }

        function redirectAI(reason) {
            const customText = document.getElementById('custom-steering').value;
            console.log(`AI Redirected: ${reason} - ${customText}`);
            
            // UI Feedback
            const hud = document.getElementById('agent-hud');
            const correction = document.createElement('div');
            correction.style = "background: rgba(234, 67, 53, 0.1); border-left: 3px solid #ea4335; padding: 12px; margin-top: 15px; border-radius: 4px; font-size: 12px; color: #ea4335;";
            correction.innerHTML = `<strong>USER INTERVENTION:</strong> ${reason} ${customText ? ': ' + customText : ''}`;
            hud.appendChild(correction);

            closeIntervention();
            if (editor) editor.updateOptions({ readOnly: false });
        }

        /* --- Custom Agent Loader Logic --- */
        const dropZone = document.getElementById('agent-drop-zone');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, e => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        dropZone.addEventListener('drop', e => {
            const dt = e.dataTransfer;
            const file = dt.files[0];
            handleAgentFile(file);
        });

        function handleAgentFile(file) {
            if (!file.name.endsWith('.py')) {
                alert('Please drop a Python (.py) file.');
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                
                // Extract Class Name
                const classMatch = content.match(/class\s+(\w+)\(/);
                const className = classMatch ? classMatch[1] : 'UnknownAgent';
                
                // Extract Description (docstring simulation)
                const descMatch = content.match(new RegExp('"{3}([\\s\\S]*?)"{3}')) || content.match(new RegExp("'{3}([\\s\\S]*?)'{3}"));
                const description = descMatch ? descMatch[1].trim().split('\n')[0] : 'No description provided.';

                showDetectedAgent(className, description);
            };
            reader.readAsText(file);
        }

        function showDetectedAgent(name, desc) {
            const container = document.getElementById('detected-agent-container');
            container.innerHTML = `
                <div class="agent-detected-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <h4 style="margin:0; color:var(--accent);">${name}</h4>
                        <span style="font-size:10px; background:rgba(88,166,255,0.1); padding:2px 6px; border-radius:4px;">NEW PLUGIN</span>
                    </div>
                    <p style="font-size:12px; color:var(--text-muted); line-height:1.4; margin-bottom:20px;">${desc}</p>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-premium" onclick="installAgent('${name}')" style="flex:1; padding:8px;">Install Agent</button>
                        <button class="btn-premium" onclick="document.getElementById('detected-agent-container').innerHTML=''" style="flex:1; padding:8px; background:transparent; border:1px solid var(--border);">Discard</button>
                    </div>
                </div>
            `;
            dropZone.style.display = 'none';
        }

        function installAgent(name) {
            alert(`Installing ${name}... This will register the plugin in your agent swarm.`);
            document.getElementById('detected-agent-container').innerHTML = `
                <div style="text-align:center; padding:20px; color:#34a853; font-size:13px; font-weight:600;">
                    ✓ ${name} Successfully Installed
                </div>
            `;
            setTimeout(() => {
                document.getElementById('detected-agent-container').innerHTML = '';
                dropZone.style.display = 'block';
            }, 3000);
        }

        async function loadRules() {
            const response = await fetch('/api/get_rules/');
            const rules = await response.json();
            
            let html = `
                <div style="margin-bottom: 24px;">
                    <h5 style="margin: 0 0 16px 0; color:var(--text-muted); font-size: 11px; text-transform: uppercase;">Global Constraints</h5>
                    <div class="rule-card">
                        <div class="rule-info">
                            <h4>Compliance Engine</h4>
                            <p>${rules.global_rules.substring(0, 80)}...</p>
                            <div style="margin-top: 8px; display:flex; gap: 4px;">
                                <span style="background: rgba(88,166,255,0.1); color: var(--accent); font-size: 9px; padding: 2px 6px; border-radius: 4px;">USPTO</span>
                                <span style="background: rgba(88,166,255,0.1); color: var(--accent); font-size: 9px; padding: 2px 6px; border-radius: 4px;">EPO</span>
                            </div>
                        </div>
                        <div class="rule-actions">
                            <label class="switch">
                                <input type="checkbox" checked onchange="toggleRule('Global')">
                                <span class="slider"></span>
                            </label>
                            <button class="btn-premium" onclick="testRule('Global', '${rules.global_rules.replace(/'/g, "\\'")}')" style="background:transparent; border:1px solid var(--border); padding: 4px 8px; font-size: 10px;">Test Rule</button>
                        </div>
                    </div>
                </div>
                <div>
                    <h5 style="margin: 0 0 16px 0; color:var(--text-muted); font-size: 11px; text-transform: uppercase;">Agent Personas</h5>
            `;

            for (const [agent, rule] of Object.entries(rules.agent_rules)) {
                html += `
                    <div class="rule-card">
                        <div class="rule-info">
                            <h4>${agent} Agent</h4>
                            <p>${rule.substring(0, 60)}...</p>
                        </div>
                        <div class="rule-actions">
                            <label class="switch">
                                <input type="checkbox" checked onchange="toggleRule('${agent}')">
                                <span class="slider"></span>
                            </label>
                            <button class="btn-premium" onclick="testRule('${agent}', '${rule.replace(/'/g, "\\'")}')" style="background:transparent; border:1px solid var(--border); padding: 4px 8px; font-size: 10px;">Test Rule</button>
                        </div>
                    </div>
                `;
            }
            html += '</div>';
            rulesContainer.innerHTML = html;
        }

        function toggleRule(name) {
            console.log(`Rule ${name} toggled.`);
        }

        function testRule(name, ruleText) {
            document.getElementById('simulation-overlay').style.display = 'flex';
            document.getElementById('sim-input').innerText = `DRAFTING_PROMPT: Write claim 1 for [Invention Description]...`;
            
            // Mock simulation results
            setTimeout(() => {
                document.getElementById('sim-output').innerText = `SYSTEM_MSG: [Rule Applied: ${name.toUpperCase()}]\n\nModified Prompt: Focus on ${ruleText.substring(0, 50)}... Ensure clarity.`;
            }, 800);
        }

        micBtn.onclick = async () => {
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = async () => {
                        micStatus.innerText = "Transcribing...";
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const formData = new FormData();
                        formData.append('audio', audioBlob);
                        
                        try {
                            const response = await fetch('/api/transcribe/', {
                                method: 'POST',
                                body: formData,
                                headers: {
                                    'X-CSRFToken': getCookie('csrftoken')
                                }
                            });
                            const data = await response.json();
                            if (data.status === 'success') {
                                if (editor) editor.setValue(data.text);
                                micStatus.innerText = "Transcription complete. Pushing to Interrogator...";
                                // In a real app, this would trigger the actual backend workflow
                            }
                        } catch (err) {
                            micStatus.innerText = "Transcription failed.";
                        }
                    };

                    mediaRecorder.start();
                    micBtn.style.background = "#34a853";
                    micStatus.innerText = "Recording... Click to stop.";
                } catch (err) {
                    micStatus.innerText = "Microphone access denied.";
                }
            } else {
                mediaRecorder.stop();
                micBtn.style.background = "#ea4335";
                micStatus.innerText = "Recording stopped. Processing...";
            }
        };

        const toggleCompareBtn = document.getElementById('toggle-compare');
        const toggleTreeBtn = document.getElementById('toggle-visual-tree');
        const comparisonView = document.getElementById('comparison-view');
        const editorToolbar = document.getElementById('editor-toolbar');
        const editorWrapper = document.getElementById('monaco-editor-wrapper');
        const treeContainer = document.getElementById('patent-tree-container');

        toggleTreeBtn.onclick = () => {
            if (treeContainer.style.display === 'none' || treeContainer.style.display === '') {
                // Enter Tree View
                treeContainer.style.display = 'flex';
                editorWrapper.style.display = 'none';
                toggleTreeBtn.innerText = "Back to Editor";
                toggleCompareBtn.style.display = 'none';
                renderPatentTree();
            } else {
                // Exit Tree View
                treeContainer.style.display = 'none';
                editorWrapper.style.display = 'flex';
                toggleTreeBtn.innerText = "Visual Tree";
                toggleCompareBtn.style.display = 'block';
            }
        };

        toggleCompareBtn.onclick = () => {
            const editorEl = document.getElementById('monaco-editor');
            const diffEl = document.getElementById('monaco-diff-editor');

            if (diffEl.style.display === 'none') {
                // Entering Diff Mode
                const modifiedText = editor.getValue();
                const originalText = `[FIELD OF THE INVENTION]
The present invention relates to thermal processing for food segments.

[CLAIMS]
1. A method for toasting comprising: providing a heating element.
2. The method of claim 1, further comprising a timer.
3. The method of claim 1, further comprising a sensor.`; // Mock Prior Art

                const originalModel = monaco.editor.createModel(originalText, 'patent');
                const modifiedModel = monaco.editor.createModel(modifiedText, 'patent');

                diffEditor.setModel({
                    original: originalModel,
                    modified: modifiedModel
                });

                editorEl.style.display = 'none';
                diffEl.style.display = 'block';
                toggleCompareBtn.innerText = "Back to Editor";
            } else {
                // Returning to Editor Mode
                editorEl.style.display = 'block';
                diffEl.style.display = 'none';
                toggleCompareBtn.innerText = "Split View";
            }
        };

        function renderPatentTree() {
            const container = document.getElementById('tree-canvas');
            container.innerHTML = '';
            const width = container.clientWidth || 800;
            const height = container.clientHeight || 500;

            const content = editor ? editor.getValue() : "";
            const claimsMatch = content.match(/\[CLAIMS\]([\s\S]*)/i);
            if (!claimsMatch) {
                container.innerHTML = '<div style="padding: 40px; text-align:center; color: var(--text-muted);">No [CLAIMS] section found in document.</div>';
                return;
            }

            const claimsText = claimsMatch[1];
            const lines = claimsText.split('\n');
            const claims = [];
            
            // Basic Parsing of Claim Dependencies
            lines.forEach(line => {
                const match = line.match(/^(\d+)\.\s+(.*)/);
                if (match) {
                    const id = match[1];
                    const text = match[2];
                    const depMatch = text.match(/claim\s+(\d+)/i);
                    const parentId = depMatch ? depMatch[1] : null;
                    claims.push({ id, name: `Claim ${id}`, parent: parentId, text: text });
                }
            });

            if (claims.length === 0) {
                container.innerHTML = '<div style="padding: 40px; text-align:center; color: var(--text-muted);">No numbered claims detected.</div>';
                return;
            }

            // Build Hierarchy
            const dataMap = claims.reduce((map, node) => {
                map[node.id] = { ...node, children: [] };
                return map;
            }, {});

            const treeData = [];
            claims.forEach(node => {
                if (node.parent && dataMap[node.parent]) {
                    dataMap[node.parent].children.push(dataMap[node.id]);
                } else {
                    // Check if claim is orphaned (mentions a parent that doesn't exist)
                    if (node.parent && !dataMap[node.parent]) {
                        dataMap[node.id].orphan = true;
                    }
                    treeData.push(dataMap[node.id]);
                }
            });

            // If we have multiple roots (independent claims), wrap them
            const root = { name: "Patent Application", children: treeData };

            const svg = d3.select("#tree-canvas").append("svg")
                .attr("width", "100%")
                .attr("height", "100%")
                .attr("viewBox", `0 0 ${width} ${height}`)
                .append("g")
                .attr("transform", "translate(120,0)");

            const treeLayout = d3.tree().size([height - 60, width - 250]);
            const d3Root = d3.hierarchy(root);
            treeLayout(d3Root);

            // Links
            svg.selectAll(".link")
                .data(d3Root.links().filter(d => d.source.depth > 0)) // Only show links from real claims, not virtual root
                .enter().append("path")
                .attr("class", d => `link ${(d.target.data.orphan || d.source.data.orphan) ? 'orphan' : ''}`)
                .attr("d", d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x));

            // Nodes
            const node = svg.selectAll(".node")
                .data(d3Root.descendants().slice(1)) // Skip the virtual root
                .enter().append("g")
                .attr("class", d => `node ${d.data.orphan ? 'orphan' : ''}`)
                .attr("transform", d => `translate(${d.y},${d.x})`);

            node.append("circle").attr("r", 7)
                .on("mouseover", function(e, d) {
                    // Tooltip logic could go here
                });

            node.append("text")
                .attr("dy", ".35em")
                .attr("x", d => d.children ? -14 : 14)
                .style("text-anchor", d => d.children ? "end" : "start")
                .text(d => d.data.name);
        }

        function renderComparison() {
            const text = editor ? editor.getValue() : "";
            const claimsMatch = text.match(/\[CLAIMS\]([\s\S]*)/i);
            if (!claimsMatch) return;

            const claimsText = claimsMatch[1];
            const lines = claimsText.split('\n');
            let html = '<div style="padding: 20px;"><h3>Comparative Alignment</h3>';
            
            lines.forEach((line, i) => {
                if (line.trim().length === 0) return;
                
                // Atomic element splitting simulation
                const elements = line.split(/[,;:]/);
                html += `<div style="margin-bottom: 10px; opacity: 0.8; font-size: 11px; color: var(--text-muted);">Line ${i+1}</div>`;
                
                elements.forEach(el => {
                    const trimmed = el.trim();
                    if (!trimmed) return;
                    
                    // Mocking novelty detection (Feature Set 5 logic)
                    const isNovel = trimmed.toLowerCase().includes("laser") || trimmed.toLowerCase().includes("rasterizer");
                    const statusClass = isNovel ? "novel" : "";
                    const bridgeId = trimmed.toLowerCase().includes("bread") ? "US-1111111-B2" : 
                                   trimmed.toLowerCase().includes("carriage") ? "US-1111111-B2" : null;

                    html += `
                        <span class="clause-item ${statusClass}" 
                              data-bridge="${bridgeId || ''}"
                              onmouseover="highlightPriorArt('${bridgeId}')" 
                              onmouseout="clearHighlights()">
                            ${trimmed} ${isNovel ? '<span style="font-size: 10px; color: #34a853; font-weight: bold; margin-left: 5px;">[NOVEL]</span>' : ''}
                        </span>
                    `;
                });
            });
            
            html += '</div>';
            comparisonView.innerHTML = html;
        }

        function highlightPriorArt(id) {
            if (!id) return;
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                if (card.innerText.includes(id)) {
                    card.classList.add('prior-art-highlight');
                }
            });
        }

        function clearHighlights() {
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => card.classList.remove('prior-art-highlight'));
        }

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        function updateRiskScore(claims, hasPriorArtConflict, hasBannedWords, hasAntecedentErrors) {
            const red = document.getElementById('light-red');
            const yellow = document.getElementById('light-yellow');
            const green = document.getElementById('light-green');
            const summary = document.getElementById('risk-summary');

            // Reset lights
            red.style.background = "#331111"; red.style.boxShadow = "none";
            yellow.style.background = "#333311"; yellow.style.boxShadow = "none";
            green.style.background = "#113311"; green.style.boxShadow = "none";

            if (hasPriorArtConflict) {
                red.style.background = "#ff4444";
                red.style.boxShadow = "0 0 10px #ff4444";
                summary.innerText = "High Risk: Prior Art Conflict Detected";
                summary.style.color = "#ff4444";
            } else if (hasBannedWords) {
                red.style.background = "#ff4444";
                red.style.boxShadow = "0 0 10px #ff4444";
                summary.innerText = "High Risk: Indefinite Language Found";
                summary.style.color = "#ff4444";
            } else if (claims.toLowerCase().includes("comprising") || hasAntecedentErrors) {
                yellow.style.background = "#ffbb33";
                yellow.style.boxShadow = "0 0 10px #ffbb33";
                summary.innerText = "Medium Risk: Broad Terminology / Minor Syntax Issues";
                summary.style.color = "#ffbb33";
            } else {
                green.style.background = "#00c851";
                green.style.boxShadow = "0 0 10px #00c851";
                summary.innerText = "Low Risk: Claims Defensible";
                summary.style.color = "#00c851";
            }
        }

        // Simulate premium data loading
        setTimeout(() => {
            const priorArt = document.getElementById('prior-art-content');
            priorArt.innerHTML = `
                <div class="card">
                    <h4>US-1111111-B2</h4>
                    <p>Method and apparatus for targeted thermal processing of food samples using directed energy beams.</p>
                </div>
                <div class="card">
                    <h4>JP-2023001-A</h4>
                    <p>High-precision raster scanning for surface carbonization of organic substrates.</p>
                </div>
                <div class="card">
                    <h4>MPEP § 2106</h4>
                    <p>Subject Matter Eligibility: Analysis of software-controlled heating elements under Alice/Mayo framework.</p>
                </div>
            `;
            
            const claimsText = `[FIELD OF THE INVENTION]
The present invention relates generally to precision thermal processing and more specifically to systems comprising laser-bread interaction.

[CLAIMS]
1. A method for toasting comprising: providing a laser pattern toaster.
2. The method of claim 1, further comprising approximately 50 infrared rasterizers.
3. The method of claim 1, further comprising micro-controller.
4. The method of claim 1, further comprising safety sensor.
5. The method of claim 1, further comprising feedback loop.

7. A system comprising: a processor; and a laser pattern toaster controlled by the processor.
8. The system of claim 7, further comprising infrared rasterizer.`;
            
            if (editor) editor.setValue(claimsText);
            
            // Mock dynamic persona shifts
            setTimeout(() => setActivePersona('research', 'Research Mode', '🔍'), 1000);
            setTimeout(() => setActivePersona('adversarial', 'Adversarial Mode', '⚖️'), 5000);
            
            // Mock risk assessment
            updateRiskScore(claimsText, false, false, false);
        }, 2000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
