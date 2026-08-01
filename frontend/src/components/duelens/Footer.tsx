import { ShieldCheck } from "lucide-react";

export function Footer() {
  return (
    <footer id="about" className="border-t border-border bg-muted/40">
      <div className="mx-auto grid max-w-6xl gap-8 px-5 py-14 md:grid-cols-[1.5fr_1fr_1fr]">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <ShieldCheck className="size-4" />
            </span>
            <span className="font-display text-base font-bold">Duelens</span>
          </div>
          <p className="mt-3 max-w-sm text-sm text-muted-foreground">
            Cross-document financial consistency checks for investors. Built as a prototype — all
            data shown is illustrative.
          </p>
        </div>
        <div>
          <p className="text-sm font-semibold">Product</p>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li>
              <a className="hover:text-foreground" href="#features">
                Features
              </a>
            </li>
            <li>
              <a className="hover:text-foreground" href="#workflow">
                Workflow
              </a>
            </li>
            <li>
              <a className="hover:text-foreground" href="#upload">
                Upload
              </a>
            </li>
          </ul>
        </div>
        <div>
          <p className="text-sm font-semibold">Company</p>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li>About</li>
            <li>Security</li>
            <li>Contact</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-border py-5 text-center text-xs text-muted-foreground">
        © {new Date().getFullYear()} Duelens. Prototype demo.
      </div>
    </footer>
  );
}
