export default function CapturGuidePage() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Recording Guide</h1>
      <p className="text-gray-600 mb-8">
        Follow these guidelines to get the best analysis results from your swing videos.
      </p>

      <div className="space-y-6">
        <Section title="Camera Position">
          <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700">
            <li>Place camera at <strong>hip height</strong>, perpendicular to the batter (side view)</li>
            <li>Distance: <strong>8-12 feet</strong> from the hitter</li>
            <li>The full body must be visible in frame from feet to head throughout the entire swing</li>
            <li>Do not zoom in too tight &mdash; leave room for the full swing arc</li>
          </ul>
        </Section>

        <Section title="Lighting">
          <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700">
            <li>Record in <strong>well-lit</strong> conditions (outdoor daylight is best)</li>
            <li>Avoid backlighting (do not point camera toward the sun or bright windows)</li>
            <li>Indoor cages: ensure overhead lighting is bright and even</li>
            <li>Avoid shadows across the hitter&apos;s body</li>
          </ul>
        </Section>

        <Section title="Video Settings">
          <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700">
            <li><strong>60 fps or higher</strong> recommended (check phone camera settings)</li>
            <li>240 fps slow-motion mode is ideal for frame-level analysis</li>
            <li>Landscape orientation</li>
            <li>Stable camera &mdash; use a tripod or prop the phone against something solid</li>
          </ul>
        </Section>

        <Section title="Swing Recording">
          <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700">
            <li>Record <strong>one swing per clip</strong> for best results</li>
            <li>Start recording <strong>2 seconds before</strong> the swing begins</li>
            <li>Continue recording <strong>1 second after</strong> the follow-through</li>
            <li>Keep clips short: 3-5 seconds is ideal</li>
          </ul>
        </Section>

        <Section title="Clothing">
          <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700">
            <li>Avoid very loose or baggy clothing &mdash; it can obscure joint positions</li>
            <li>Fitted practice wear produces the cleanest landmark tracking</li>
            <li>Contrasting colors between clothing and background help</li>
          </ul>
        </Section>

        <Section title="For Slap Hitters">
          <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700">
            <li>Make sure the <strong>full crossover and movement path</strong> is visible</li>
            <li>Camera may need to be positioned slightly further back to capture the travel</li>
            <li>The full heel plant must be visible &mdash; do not cut off the feet</li>
          </ul>
        </Section>

        <Section title="Common Mistakes">
          <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700">
            <li>Camera too close &mdash; body exits the frame during swing</li>
            <li>Feet cut off at the bottom of the frame</li>
            <li>Shaky handheld recording &mdash; use a tripod</li>
            <li>Multiple swings in one clip &mdash; trim to one swing per upload</li>
            <li>Poor lighting &mdash; dim cages or backlit outdoor settings</li>
          </ul>
        </Section>
      </div>

      <div className="mt-8 bg-scout-50 rounded-lg p-6">
        <h3 className="font-semibold mb-2">Quick Checklist</h3>
        <div className="grid grid-cols-2 gap-2 text-sm text-gray-700">
          {[
            'Side view at hip height',
            '8-12 feet away',
            'Full body visible (feet to head)',
            '60+ fps (240 fps ideal)',
            'Landscape orientation',
            'Stable camera / tripod',
            'Good lighting, no backlighting',
            'One swing per clip',
            'Start 2s before, end 1s after',
            'Fitted clothing',
          ].map((item, i) => (
            <label key={i} className="flex items-center gap-2">
              <input type="checkbox" className="rounded" />
              {item}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="font-semibold mb-3">{title}</h2>
      {children}
    </div>
  );
}
