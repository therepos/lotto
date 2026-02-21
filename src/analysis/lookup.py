TITLE = "Check Your Combination (Interactive)"
ORDER = 5

def generate(df):
    # We return raw HTML + a script tag. GitHub Pages renders raw HTML in Markdown.
    return """
## Check Your Combination (Interactive)

Enter six numbers (1–49). Order doesn’t matter.

<div id="combo-lookup" style="margin: 1rem 0;">
  <input id="n1" type="number" min="1" max="49" style="width:4rem;"> 
  <input id="n2" type="number" min="1" max="49" style="width:4rem;">
  <input id="n3" type="number" min="1" max="49" style="width:4rem;">
  <input id="n4" type="number" min="1" max="49" style="width:4rem;">
  <input id="n5" type="number" min="1" max="49" style="width:4rem;">
  <input id="n6" type="number" min="1" max="49" style="width:4rem;">
  <button id="lookup-btn">Check history</button>
  <div id="lookup-result" style="margin-top:0.5rem;font-weight:600;"></div>
</div>

<script src="/analysis/lookup.js"></script>
"""
