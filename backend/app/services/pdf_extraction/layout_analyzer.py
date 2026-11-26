"""
Layout and Color Analyzer
Dynamically extracts:
1. Glance grid items: desk names, exact fill colors (#e8b31b, #3c8b57, #df6a12), and text directly from vector drawings.
2. Exact Card background fills (Navy #01093d vs White #ffffff vs Amber/Orange) directly from vector drawings.
"""

import fitz

def get_layout_and_colors(pdf_path: str):
    doc = fitz.open(pdf_path)
    
    # ── 1. Glance grid on Page 1 ──
    glance_items = []
    p1 = doc[0]
    p1_drawings = p1.get_drawings()
    tiles = []
    for d in p1_drawings:
        r = d['rect']
        if 215 <= r.y0 <= 255 and 30 <= r.width <= 75 and 20 <= r.height <= 45 and d.get('fill'):
            fill = d['fill']
            hex_fill = f"#{int(fill[0]*255):02x}{int(fill[1]*255):02x}{int(fill[2]*255):02x}"
            if hex_fill != "#f5f6fa" and hex_fill != "#ffffff":
                tiles.append({'x0': r.x0, 'x1': r.x1, 'y0': r.y0, 'y1': r.y1, 'color': hex_fill})
    
    tiles.sort(key=lambda t: t['x0'])
    
    p1_words = p1.get_text('words')
    for t in tiles:
        tile_words = [w for w in p1_words if (t['x0'] - 6) <= w[0] <= (t['x1'] + 6) and (t['y0'] - 4) <= w[1] <= (t['y1'] + 4)]
        tile_words.sort(key=lambda w: (w[1], w[0]))
        if tile_words:
            desk_name = tile_words[0][4]
            desc = " ".join(w[4] for w in tile_words[1:])
        else:
            desk_name = "DESK"
            desc = ""
        glance_items.append({
            'name': desk_name,
            'color': t['color'],
            'text': desc
        })

    # ── 2. Card background colors ──
    def detect_box_bg(page_idx, target_rect):
        page = doc[page_idx]
        drawings = page.get_drawings()
        tx0, ty0, tx1, ty1 = target_rect
        for d in drawings:
            r = d['rect']
            if not d.get('fill'):
                continue
            # Check overlap > 70%
            if r.x0 <= tx0 + 15 and r.y0 <= ty0 + 15 and r.x1 >= tx1 - 15 and r.y1 >= ty1 - 15:
                fill = d['fill']
                hex_fill = f"#{int(fill[0]*255):02x}{int(fill[1]*255):02x}{int(fill[2]*255):02x}"
                if hex_fill != "#ffffff":
                    return hex_fill
        return "#ffffff"

    card_bgs = {
        'p1_lead': detect_box_bg(0, (25, 270, 560, 500)),
        'p1_left': detect_box_bg(0, (25, 520, 290, 800)),
        'p1_right': detect_box_bg(0, (300, 520, 560, 800)),
        'p2_top': detect_box_bg(1, (25, 35, 570, 250)),
        'p2_ml': detect_box_bg(1, (25, 260, 290, 530)),
        'p2_mr': detect_box_bg(1, (300, 260, 560, 530)),
        'p2_bl': detect_box_bg(1, (25, 550, 290, 800)),
        'p2_br': detect_box_bg(1, (300, 550, 560, 800)),
    }

    return glance_items, card_bgs

if __name__ == '__main__':
    items, bgs = get_layout_and_colors('sample-data/pulse_reference.pdf')
    print('GLANCE TILES EXTRACTED:', len(items))
    for it in items:
        print('  ', it)
    print('CARD BACKGROUNDS DETECTED:')
    for k, v in bgs.items():
        print(f'   {k}: {v}')
