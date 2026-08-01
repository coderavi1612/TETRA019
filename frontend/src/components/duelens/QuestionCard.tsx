import { motion } from "motion/react";
import { MessageCircleQuestion } from "lucide-react";

export function QuestionCard({
  index,
  question,
}: {
  index: number;
  question: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ y: -3 }}
      className="surface flex gap-4 p-6"
    >
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary-soft text-primary">
        <MessageCircleQuestion className="size-4" />
      </span>
      <div>
        <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
          Question {index + 1}
        </p>
        <p className="mt-1.5 text-sm font-medium">{question}</p>
      </div>
    </motion.div>
  );
}
