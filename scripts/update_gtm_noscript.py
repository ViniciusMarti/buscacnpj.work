import os

gtm_head = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WWPBCTLJ');</script>
<!-- End Google Tag Manager -->
"""

gtm_noscript = """<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WWPBCTLJ"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
"""

def update_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        modified = False

        # Add noscript tag after body if not already present
        if '<body' in content and 'GTM-WWPBCTLJ' not in content.split('<body', 1)[1]:
            # find the end of body tag
            body_end = content.find('>', content.find('<body'))
            if body_end != -1:
                content = content[:body_end+1] + '\n' + gtm_noscript + content[body_end+1:]
                modified = True
                
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

search_dir = r"c:\Users\marti\Documents\repositorio\buscacnpjgratis"
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith('.php') or file.endswith('.html'):
            filepath = os.path.join(root, file)
            update_file(filepath)
