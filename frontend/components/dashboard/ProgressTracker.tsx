import { CheckCircle, Circle } from 'lucide-react'

interface ProgressTrackerProps {
  currentStep: number
}

const steps = [
  { id: 1, name: 'Generate Script', description: 'Create AI-powered content' },
  { id: 2, name: 'Preview Images', description: 'Review generated images' },
  { id: 3, name: 'Create Video', description: 'Assemble final video' },
  { id: 4, name: 'Download', description: 'Get your TikTok video' },
]

export default function ProgressTracker({ currentStep }: ProgressTrackerProps) {
  return (
    <nav aria-label="Progress">
      <ol role="list" className="flex items-center">
        {steps.map((step, stepIdx) => (
          <li key={step.name} className={stepIdx !== steps.length - 1 ? 'pr-8 sm:pr-20 flex-1' : ''}>
            <div className="flex items-center">
              <div className="relative flex items-center justify-center">
                {step.id < currentStep ? (
                  <CheckCircle className="h-8 w-8 text-green-600" />
                ) : step.id === currentStep ? (
                  <div className="h-8 w-8 rounded-full border-2 border-primary bg-primary">
                    <span className="flex h-full w-full items-center justify-center text-white text-sm">
                      {step.id}
                    </span>
                  </div>
                ) : (
                  <Circle className="h-8 w-8 text-gray-300" />
                )}
              </div>
              {stepIdx !== steps.length - 1 && (
                <div className="ml-4 flex-1">
                  <div className={`h-0.5 ${step.id < currentStep ? 'bg-green-600' : 'bg-gray-200'}`} />
                </div>
              )}
            </div>
            <div className="mt-2">
              <span className="text-xs font-semibold tracking-wide uppercase text-gray-500">
                {step.name}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </nav>
  )
}