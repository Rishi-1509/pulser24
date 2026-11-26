import { useState, useEffect } from 'react';
import { getBrandingSettings, saveBrandingSettings } from '../services/api';
import type { BrandingSettings } from '../types/api';

export default function SettingsPage() {
  const [settings, setSettings] = useState<BrandingSettings>({
    app_title: 'Pulse R24 Email Publishing Studio',
    bulletin_name: 'PULSE R24',
    primary_color: '#0f2d59',
    secondary_color: '#2563eb',
    accent_color: '#d97706',
    font_family: 'Arial, Helvetica, sans-serif',
    max_email_width: 650,
    social_links: {
      x_twitter: 'https://twitter.com/issp_india',
      linkedin: 'https://www.linkedin.com/company/issp-india',
      youtube: 'https://www.youtube.com/@issp_india',
      website: 'https://rru.ac.in',
    },
    ai_declaration:
      'AI Declaration: This publication incorporates automated collection and AI-assisted compilation. All links, sources, and factual narratives have been deterministic-extracted and human-reviewed.',
    institutional_attribution:
      'Published by the Center for Security & Intelligence Studies in collaboration with ISSP, RRU Puducherry, and CAREVIA.',
  });

  const [loading, setLoading] = useState(true);
  const [savedMsg, setSavedMsg] = useState(false);

  useEffect(() => {
    setLoading(true);
    getBrandingSettings()
      .then(setSettings)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    try {
      await saveBrandingSettings(settings);
      setSavedMsg(true);
      setTimeout(() => setSavedMsg(false), 2500);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save settings');
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading settings...</div>;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Pulse R24 Branding & System Settings</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure default bulletin identity, social media destinations, and institutional declarations.
          </p>
        </div>
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs rounded-xl shadow-xs transition"
        >
          {savedMsg ? '✓ Saved!' : 'Save Settings'}
        </button>
      </div>

      {savedMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-semibold">
          ✓ Branding configurations saved successfully and applied to all future email generations.
        </div>
      )}

      {/* Brand Identity Section */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Publication Identity</h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Bulletin Name</label>
            <input
              type="text"
              value={settings.bulletin_name}
              onChange={(e) => setSettings({ ...settings, bulletin_name: e.target.value })}
              className="w-full text-xs p-2 rounded-lg border border-slate-300"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Application Title</label>
            <input
              type="text"
              value={settings.app_title}
              onChange={(e) => setSettings({ ...settings, app_title: e.target.value })}
              className="w-full text-xs p-2 rounded-lg border border-slate-300"
            />
          </div>
        </div>

        {/* Colors */}
        <div className="grid grid-cols-3 gap-4 pt-2">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Primary Brand Color</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={settings.primary_color}
                onChange={(e) => setSettings({ ...settings, primary_color: e.target.value })}
                className="w-8 h-8 rounded border border-slate-300 cursor-pointer p-0.5"
              />
              <span className="text-xs font-mono">{settings.primary_color}</span>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Secondary Color</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={settings.secondary_color}
                onChange={(e) => setSettings({ ...settings, secondary_color: e.target.value })}
                className="w-8 h-8 rounded border border-slate-300 cursor-pointer p-0.5"
              />
              <span className="text-xs font-mono">{settings.secondary_color}</span>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Accent Color</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={settings.accent_color}
                onChange={(e) => setSettings({ ...settings, accent_color: e.target.value })}
                className="w-8 h-8 rounded border border-slate-300 cursor-pointer p-0.5"
              />
              <span className="text-xs font-mono">{settings.accent_color}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Social Media Channels */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          Social Media & Web Destinations
        </h3>
        <p className="text-[11px] text-slate-500">
          These URLs are linked to the social media icons in the generated email footer.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Object.entries(settings.social_links).map(([key, val]) => (
            <div key={key}>
              <label className="text-xs font-semibold text-slate-700 block mb-1 capitalize">
                {key.replace('_', ' ')}
              </label>
              <input
                type="text"
                value={val}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    social_links: { ...settings.social_links, [key]: e.target.value },
                  })
                }
                className="w-full text-xs p-2 rounded-lg border border-slate-300 font-mono"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Declarations & Attribution */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          Institutional & AI Disclaimers
        </h3>

        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">
            Institutional Attribution Text
          </label>
          <textarea
            rows={2}
            value={settings.institutional_attribution}
            onChange={(e) => setSettings({ ...settings, institutional_attribution: e.target.value })}
            className="w-full text-xs p-2 rounded-lg border border-slate-300"
          />
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-1">
            AI Usage Declaration
          </label>
          <textarea
            rows={2}
            value={settings.ai_declaration}
            onChange={(e) => setSettings({ ...settings, ai_declaration: e.target.value })}
            className="w-full text-xs p-2 rounded-lg border border-slate-300"
          />
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
        >
          {savedMsg ? '✓ Settings Saved' : 'Save All Settings'}
        </button>
      </div>
    </div>
  );
}
