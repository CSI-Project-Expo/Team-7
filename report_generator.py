"""
===========================================================
FILE: report_generator.py
PURPOSE: Generate TXT and PDF session reports
SYSTEM: Kali Linux
MEMBER: 4 (Logging & Reports)
===========================================================
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Optional


class ReportGenerator:
    """
    Generates professional session reports in TXT and PDF.
    Summarizes game stats, attacks, blocks, achievements.
    """
    
    def __init__(self, output_folder: str = "reports"):
        self.output_folder = output_folder
        self.report_data = {}
        self._ensure_folder()
        
        # Check PDF capability
        self.pdf_available = False
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            self.pdf_available = True
        except ImportError:
            pass
        
        print(f"[REPORT] ✅ Initialized (PDF: {'Yes' if self.pdf_available else 'No'})")
    
    def _ensure_folder(self):
        """Create output folder if missing."""
        try:
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)
        except Exception as e:
            print(f"[REPORT] ⚠️ Folder error: {e}")
    
    # ════════════════════════════════════════
    # DATA COLLECTION
    # ════════════════════════════════════════
    
    def collect_data(
        self,
        game_stats: Dict = None,
        score_stats: Dict = None,
        wave_stats: Dict = None,
        achievements: List = None,
        blocked_ips: List = None,
        events: List = None,
        sniffer_stats: Dict = None,
        grade: str = "?"
    ):
        """Collect all data for report generation."""
        
        self.report_data = {
            'generated_at': "N/A",
            'session_id': "SESSION-DATA",
            
            # Game
            'game_time': game_stats.get('game_time', 0) if game_stats else 0,
            'final_health': game_stats.get('health', 0) if game_stats else 0,
            'packets_processed': game_stats.get('packets_processed', 0) if game_stats else 0,
            'survived': game_stats.get('health', 0) > 0 if game_stats else False,
            
            # Score
            'final_score': score_stats.get('score', 0) if score_stats else 0,
            'high_score': score_stats.get('high_score', 0) if score_stats else 0,
            'max_combo': score_stats.get('max_combo', 0) if score_stats else 0,
            'total_blocked': score_stats.get('total_blocked', 0) if score_stats else 0,
            'malicious_blocked': score_stats.get('malicious_blocked', 0) if score_stats else 0,
            
            # Waves
            'waves_completed': wave_stats.get('waves_completed', 0) if wave_stats else 0,
            'highest_wave': wave_stats.get('current_wave', 0) if wave_stats else 0,
            
            # Achievements
            'achievements': achievements or [],
            
            # Defense
            'blocked_ips': blocked_ips or [],
            
            # Events
            'events': events or [],
            
            # Sniffer
            'sniffer_stats': sniffer_stats or {},
            
            # Grade
            'grade': grade
        }
    
    # ════════════════════════════════════════
    # FORMAT TIME
    # ════════════════════════════════════════
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"
    
    # ════════════════════════════════════════
    # TXT REPORT
    # ════════════════════════════════════════
    
    def generate_txt(self, filename: str = None) -> str:
        """
        Generate a TXT report file.
        
        Returns:
            Path to generated file.
        """
        
        d = self.report_data
        
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mission_report_{ts}.txt"
        
        filepath = os.path.join(self.output_folder, filename)
        
        # Build report content
        lines = []
        
        # Header
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + "PACKET DEFENDER — MISSION REPORT".center(58) + "║")
        lines.append("║" + "Cyber Defense Simulation".center(58) + "║")
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("║" + f"  Generated: {d.get('generated_at', 'N/A')}".ljust(58) + "║")
        lines.append("║" + f"  Session:   {d.get('session_id', 'N/A')}".ljust(58) + "║")
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        # Result
        result = "MISSION COMPLETE" if d.get('survived') else "NETWORK COMPROMISED"
        lines.append(f"  ┌─────────────────────────────────────┐")
        lines.append(f"  │  RESULT: {result:28s}│")
        lines.append(f"  │  GRADE:  {d.get('grade', '?'):28s}│")
        lines.append(f"  │  TIME:   {self._format_time(d.get('game_time', 0)):28s}│")
        lines.append(f"  └─────────────────────────────────────┘")
        lines.append("")
        
        # Score Section
        lines.append("  ── SCORE ──────────────────────────────")
        lines.append(f"  Final Score      : {d.get('final_score', 0)}")
        lines.append(f"  High Score       : {d.get('high_score', 0)}")
        new_hs = "★ NEW HIGH SCORE ★" if d.get('final_score', 0) >= d.get('high_score', 0) else ""
        if new_hs:
            lines.append(f"                     {new_hs}")
        lines.append(f"  Max Combo        : {d.get('max_combo', 0)}x")
        lines.append("")
        
        # Defense Section
        lines.append("  ── DEFENSE ────────────────────────────")
        lines.append(f"  Packets Processed: {d.get('packets_processed', 0)}")
        lines.append(f"  Threats Blocked  : {d.get('total_blocked', 0)}")
        lines.append(f"  Malicious Blocked: {d.get('malicious_blocked', 0)}")
        lines.append(f"  Final Health     : {d.get('final_health', 0)}%")
        lines.append("")
        
        # Wave Section
        lines.append("  ── WAVES ──────────────────────────────")
        lines.append(f"  Waves Completed  : {d.get('waves_completed', 0)}")
        lines.append(f"  Highest Wave     : {d.get('highest_wave', 0)}")
        lines.append("")
        
        # Blocked IPs
        blocked = d.get('blocked_ips', [])
        if blocked:
            lines.append("  ── BLOCKED IPs ────────────────────────")
            for ip in blocked[:20]:
                lines.append(f"    🚫 {ip}")
            if len(blocked) > 20:
                lines.append(f"    ... and {len(blocked) - 20} more")
            lines.append("")
        
        # Achievements
        achs = d.get('achievements', [])
        if achs:
            lines.append("  ── ACHIEVEMENTS ───────────────────────")
            for a in achs:
                if hasattr(a, 'name'):
                    lines.append(f"    🏆 {a.name}")
                elif isinstance(a, dict):
                    lines.append(f"    🏆 {a.get('name', 'Unknown')}")
                else:
                    lines.append(f"    🏆 {a}")
            lines.append("")
        
        # Sniffer Stats
        sniffer = d.get('sniffer_stats', {})
        if sniffer:
            lines.append("  ── NETWORK ANALYSIS ───────────────────")
            lines.append(f"  Packets Captured : {sniffer.get('total_captured', 0)}")
            lines.append(f"  Unique Sources   : {sniffer.get('unique_sources', 0)}")
            lines.append(f"  Peak PPS         : {sniffer.get('peak_pps', 0)}")
            
            breakdown = sniffer.get('threat_breakdown', {})
            if breakdown:
                lines.append(f"  Safe             : {breakdown.get('safe', 0)}")
                lines.append(f"  Suspicious       : {breakdown.get('suspicious', 0)}")
                lines.append(f"  Hostile          : {breakdown.get('hostile', 0)}")
                lines.append(f"  Critical         : {breakdown.get('critical', 0)}")
            lines.append("")
        
        # Recent Events
        events = d.get('events', [])
        if events:
            lines.append("  ── RECENT EVENTS ──────────────────────")
            for evt in events[-15:]:
                if isinstance(evt, dict):
                    tp = evt.get('type', 'INFO')
                    msg = evt.get('message', '')
                    lines.append(f"    {tp:8s} {msg[:40]}")
                else:
                    lines.append(f"    {evt}")
            lines.append("")
        
        # Footer
        lines.append("═" * 60)
        lines.append("  Generated by PACKET DEFENDER v1.0")
        lines.append("  Cyber Defense Simulation Game")
        lines.append("═" * 60)
        
        # Write file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"[REPORT] ✅ TXT report saved: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"[REPORT] ❌ TXT generation failed: {e}")
            return ""
    
    # ════════════════════════════════════════
    # PDF REPORT
    # ════════════════════════════════════════
    
    def generate_pdf(self, filename: str = None) -> str:
        """
        Generate a PDF report.
        Requires: pip install reportlab
        
        Returns:
            Path to generated file.
        """
        
        if not self.pdf_available:
            print("[REPORT] ⚠️ reportlab not installed, generating TXT instead")
            return self.generate_txt(filename)
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.colors import HexColor
        except ImportError:
            return self.generate_txt(filename)
        
        d = self.report_data
        
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mission_report_{ts}.pdf"
        
        filepath = os.path.join(self.output_folder, filename)
        
        try:
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # Colors
            dark_bg = HexColor("#0a0f1a")
            neon_blue = HexColor("#00c8ff")
            neon_green = HexColor("#00ff96")
            neon_red = HexColor("#ff3250")
            white = HexColor("#ffffff")
            gray = HexColor("#9696b4")
            
            # Background
            c.setFillColor(dark_bg)
            c.rect(0, 0, width, height, fill=True)
            
            # Title
            c.setFillColor(neon_blue)
            c.setFont("Helvetica-Bold", 28)
            c.drawCentredString(width / 2, height - 60, "PACKET DEFENDER")
            
            c.setFont("Helvetica", 14)
            c.setFillColor(gray)
            c.drawCentredString(width / 2, height - 85, "Mission Report — Cyber Defense Simulation")
            
            # Divider
            c.setStrokeColor(neon_blue)
            c.setLineWidth(2)
            c.line(50, height - 100, width - 50, height - 100)
            
            y = height - 130
            
            # Result box
            result = "MISSION COMPLETE" if d.get('survived') else "NETWORK COMPROMISED"
            result_color = neon_green if d.get('survived') else neon_red
            
            c.setFillColor(result_color)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(60, y, f"Result: {result}")
            y -= 30
            
            c.setFont("Helvetica-Bold", 18)
            c.drawString(60, y, f"Grade: {d.get('grade', '?')}")
            c.drawString(250, y, f"Time: {self._format_time(d.get('game_time', 0))}")
            y -= 40
            
            # Score Section
            c.setFillColor(neon_blue)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(60, y, "─── SCORE ───")
            y -= 25
            
            c.setFillColor(white)
            c.setFont("Helvetica", 12)
            
            score_items = [
                f"Final Score: {d.get('final_score', 0)}",
                f"High Score: {d.get('high_score', 0)}",
                f"Max Combo: {d.get('max_combo', 0)}x",
            ]
            
            for item in score_items:
                c.drawString(80, y, item)
                y -= 20
            y -= 10
            
            # Defense Section
            c.setFillColor(neon_green)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(60, y, "─── DEFENSE ───")
            y -= 25
            
            c.setFillColor(white)
            c.setFont("Helvetica", 12)
            
            defense_items = [
                f"Packets Processed: {d.get('packets_processed', 0)}",
                f"Threats Blocked: {d.get('total_blocked', 0)}",
                f"Malicious Blocked: {d.get('malicious_blocked', 0)}",
                f"Final Health: {d.get('final_health', 0)}%",
                f"Waves Completed: {d.get('waves_completed', 0)}",
            ]
            
            for item in defense_items:
                c.drawString(80, y, item)
                y -= 20
            y -= 10
            
            # Blocked IPs
            blocked = d.get('blocked_ips', [])
            if blocked:
                c.setFillColor(neon_red)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(60, y, "─── BLOCKED IPs ───")
                y -= 25
                
                c.setFillColor(white)
                c.setFont("Helvetica", 11)
                
                for ip in blocked[:15]:
                    c.drawString(80, y, f"🚫 {ip}")
                    y -= 18
                    if y < 100:
                        break
                y -= 10
            
            # Achievements
            achs = d.get('achievements', [])
            if achs and y > 150:
                c.setFillColor(HexColor("#ffd700"))
                c.setFont("Helvetica-Bold", 16)
                c.drawString(60, y, "─── ACHIEVEMENTS ───")
                y -= 25
                
                c.setFillColor(white)
                c.setFont("Helvetica", 11)
                
                for a in achs:
                    name = a.name if hasattr(a, 'name') else (a.get('name', str(a)) if isinstance(a, dict) else str(a))
                    c.drawString(80, y, f"🏆 {name}")
                    y -= 18
                    if y < 80:
                        break
            
            # Footer
            c.setStrokeColor(neon_blue)
            c.line(50, 50, width - 50, 50)
            c.setFillColor(gray)
            c.setFont("Helvetica", 9)
            c.drawCentredString(width / 2, 35, f"Generated: {d.get('generated_at', '')} | PACKET DEFENDER v1.0")
            
            c.save()
            print(f"[REPORT] ✅ PDF report saved: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"[REPORT] ❌ PDF failed: {e}, generating TXT")
            return self.generate_txt()
    
    # ════════════════════════════════════════
    # GENERATE BOTH
    # ════════════════════════════════════════
    
    def generate_all(self) -> Dict[str, str]:
        """Generate both TXT and PDF reports."""
        
        results = {}
        results['txt'] = self.generate_txt()
        results['pdf'] = self.generate_pdf()
        return results
    
    # ════════════════════════════════════════
    # PRINT TO CONSOLE
    # ════════════════════════════════════════
    
    def print_summary(self):
        """Print a quick summary to console."""
        
        d = self.report_data
        
        result = "COMPLETE" if d.get('survived') else "COMPROMISED"
        
        print()
        print("═" * 50)
        print("         MISSION REPORT SUMMARY")
        print("═" * 50)
        print(f"  Result : {result}")
        print(f"  Grade  : {d.get('grade', '?')}")
        print(f"  Score  : {d.get('final_score', 0)}")
        print(f"  Time   : {self._format_time(d.get('game_time', 0))}")
        print(f"  Waves  : {d.get('waves_completed', 0)}")
        print(f"  Blocked: {d.get('total_blocked', 0)}")
        print("═" * 50)
        print()


# ════════════════════════════════════════
# STANDALONE TEST
# ════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("  REPORT GENERATOR — TEST")
    print("=" * 50)
    
    gen = ReportGenerator()
    
    # Fake test data
    gen.collect_data(
        game_stats={'game_time': 185.5, 'health': 0, 'packets_processed': 347},
        score_stats={'score': 4250, 'high_score': 4250, 'max_combo': 12,
                     'total_blocked': 89, 'malicious_blocked': 56},
        wave_stats={'waves_completed': 6, 'current_wave': 7},
        achievements=[{'name': 'First Blood'}, {'name': 'Guardian'}, {'name': 'Combo Master'}],
        blocked_ips=['45.33.32.156', '185.220.101.1', '89.248.167.131'],
        events=[
            {'timestamp': '12:04:33', 'type': 'ATTACK', 'message': 'DDoS detected from 45.33.32.156'},
            {'timestamp': '12:04:35', 'type': 'BLOCK', 'message': 'Blocked 45.33.32.156'},
            {'timestamp': '12:05:01', 'type': 'DEFENSE', 'message': 'Auto-defense activated'},
        ],
        grade='A'
    )
    
    gen.print_summary()
    gen.generate_txt()
    gen.generate_pdf()
    
    print("\n✅ Report generation complete!")
