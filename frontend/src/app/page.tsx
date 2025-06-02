import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">Rate My Resume</h1>
        <p className="text-center mb-8">AI-Powered Resume Analysis Tool</p>
        <div className="flex justify-center">
          <Button size="lg">Upload Resume</Button>
        </div>
      </div>
    </main>
  )
} 