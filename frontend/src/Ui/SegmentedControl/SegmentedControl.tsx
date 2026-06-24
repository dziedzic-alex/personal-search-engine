import type { SegmentedControlOption } from "./SegmentedControlOption";

import "./SegmentedControl.css";

const ICON_SIZE = 16;

interface Props {
  label: string;
  value: string;
  options: SegmentedControlOption[];
  onChange: (id: string) => void;
  isDisabled?: boolean;
}

function SegmentedControl(props: Props) {
  const { label, value, options, onChange, isDisabled = false } = props;

  function handleSelect(option: SegmentedControlOption) {
    if (option.disabled || isDisabled) {
      return;
    }

    onChange(option.id);
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLButtonElement>,
    index: number,
  ) {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
      return;
    }

    event.preventDefault();

    const direction = event.key === "ArrowRight" ? 1 : -1;
    const enabledOptions = options.filter((option) => !option.disabled);
    const currentIndex = enabledOptions.findIndex(
      (option) => option.id === options[index]?.id,
    );

    if (currentIndex === -1) {
      return;
    }

    const nextIndex =
      (currentIndex + direction + enabledOptions.length) %
      enabledOptions.length;
    const nextOption = enabledOptions[nextIndex];

    onChange(nextOption.id);
    document.getElementById(`segmented-control-${nextOption.id}`)?.focus();
  }

  return (
    <div className="segmented-control" role="radiogroup" aria-label={label}>
      {options.map((option, index) => {
        const isSelected = value === option.id;

        return (
          <button
            key={option.id}
            id={`segmented-control-${option.id}`}
            type="button"
            className={[
              "segmented-control-segment",
              isSelected ? "segmented-control-segment-selected" : "",
            ]
              .filter(Boolean)
              .join(" ")}
            role="radio"
            aria-checked={isSelected}
            disabled={isDisabled || option.disabled}
            onClick={() => {
              handleSelect(option);
            }}
            onKeyDown={(event) => {
              handleKeyDown(event, index);
            }}
          >
            {option.icon ? (
              <span className="segmented-control-segment-icon">
                <option.icon
                  size={ICON_SIZE}
                  aria-hidden
                  color={option.iconColor ?? "var(--color-text-muted)"}
                />
              </span>
            ) : null}
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

export default SegmentedControl;
