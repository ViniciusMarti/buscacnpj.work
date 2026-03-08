import os
import glob

gtm_head = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WWPBCTLJ');</script>
<!-- End Google Tag Manager -->
"""

gtm_body = """
<!-- GTM Custom Events Tracker -->
<script src="/assets/gtm-events.js" defer></script>
"""

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    if '<head>' in content and 'GTM-WWPBCTLJ' not in content:
        content = content.replace('<head>', '<head>\n' + gtm_head, 1)
        modified = True
    
    # some files might have <head ... >
    elif '<head ' in content and 'GTM-WWPBCTLJ' not in content:
        # find the end of head tag
        head_end = content.find('>', content.find('<head '))
        if head_end != -1:
            content = content[:head_end+1] + '\n' + gtm_head + content[head_end+1:]
            modified = True

    if '</body>' in content and 'gtm-events.js' not in content:
        content = content.replace('</body>', gtm_body + '\n</body>')
        modified = True
    elif '</html>' in content and 'gtm-events.js' not in content and '</body>' not in content:
        # handle case where no body exists but html ends
        content = content.replace('</html>', gtm_body + '\n</html>')
        modified = True
        
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

search_dir = r"c:\Users\marti\Documents\repositorio\buscacnpjgratis"
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith('.php') or file.endswith('.html'):
            filepath = os.path.join(root, file)
            update_file(filepath)
